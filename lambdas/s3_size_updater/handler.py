import os
import json
import re
import logging
from urllib.parse import unquote_plus, urlparse

import boto3
import pg8000

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Expect keys like: projects/{project_id}/...
PROJECT_RE = re.compile(r"^projects/(\d+)/")

s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")


def _db_url():
    name = os.environ["DB_SECRET_NAME"]
    sec = secrets.get_secret_value(SecretId=name)["SecretString"]
    try:
        obj = json.loads(sec)  # if secret is key/value JSON
        return obj.get("PB_DATABASE_URL") or obj.get("url")
    except json.JSONDecodeError:
        return sec  # plaintext


def _connect():
    url = _db_url()
    u = urlparse(url)
    return pg8000.connect(
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
        database=u.path.lstrip("/"),
        ssl_context=True,  # TLS to RDS
    )


def _sum_prefix(bucket, prefix):
    total = 0
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix}
        if token:
            kwargs["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []) or []:
            total += int(obj.get("Size", 0))
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return total


def _parse_record(rec):
    ev = rec.get("eventName", "")
    obj = (rec.get("s3") or {}).get("object") or {}
    key = unquote_plus(obj.get("key", "") or "")
    size = obj.get("size")  # present on ObjectCreated.*
    m = PROJECT_RE.match(key)
    pid = int(m.group(1)) if m else None
    if ev.startswith("ObjectCreated:"):
        delta = int(size or 0)
    elif ev.startswith("ObjectRemoved:"):
        delta = None
    else:
        delta = 0
    return {"event": ev, "project_id": pid, "key": key, "size": size, "delta": delta}


def lambda_handler(event, context):
    # Diagnostic: DB ping
    if event.get("ping_db"):
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                one = cur.fetchone()[0]
            conn.commit()
            return {"ok": True, "db": "up", "select1": one}
        finally:
            conn.close()

    bucket = os.environ["BUCKET"]
    recalc_on_delete = str(os.environ.get("RECALC_ON_DELETE", "true")).lower() == "true"

    records = event.get("Records", []) or []
    parsed = [_parse_record(r) for r in records]
    logger.info("S3 Event Parsed: %s", json.dumps(parsed))

    # Nothing relevant
    pids_to_recalc = set()
    increments = []
    for p in parsed:
        if not p["project_id"]:
            logger.warning("Skip key without project_id: %s", p["key"])
            continue
        if p["event"].startswith("ObjectCreated:") and p["delta"]:
            increments.append((p["project_id"], p["delta"]))
        elif p["event"].startswith("ObjectRemoved:"):
            pids_to_recalc.add(p["project_id"])

    if not increments and not pids_to_recalc:
        return {"ok": True, "note": "no actionable records"}

    conn = _connect()
    try:
        with conn.cursor() as cur:
            # Increment on create events
            for pid, delta in increments:
                cur.execute(
                    "UPDATE projects "
                    "SET total_size_bytes = GREATEST(COALESCE(total_size_bytes, 0) + %s, 0) "
                    "WHERE id = %s",
                    (int(delta), int(pid)),
                )

            if recalc_on_delete:
                for pid in sorted(pids_to_recalc):
                    prefix = f"projects/{pid}/"
                    new_total = _sum_prefix(bucket, prefix)
                    cur.execute(
                        "UPDATE projects SET total_size_bytes = %s WHERE id = %s",
                        (int(new_total), int(pid)),
                    )
        conn.commit()
    finally:
        conn.close()

    return {
        "ok": True,
        "created_events": len(increments),
        "recalculated_projects": len(pids_to_recalc),
    }
