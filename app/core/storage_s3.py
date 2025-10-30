from __future__ import annotations

import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client("s3", region_name=settings.AWS_REGION)


def ping_bucket() -> bool:
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=settings.S3_BUCKET)
        return True
    except ClientError as e:
        resp = e.response or {}
        meta = resp.get("ResponseMetadata", {})
        http_status = meta.get("HTTPStatusCode")
        err = resp.get("Error", {})
        err_code = err.get("Code")
        err_msg = err.get("Message")
        logger.warning("S3 ping failed (status=%s, code=%s): %s", http_status, err_code, err_msg)
        return False
    except BotoCoreError as e:
        logger.exception("S3 ping failed (boto core): %s", e)
        return False


def put_text(key: str, body: str) -> None:
    s3 = get_s3_client()
    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=body.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )
    except (ClientError, BotoCoreError) as e:
        logger.exception("S3 put_text failed (key=%s): %s", key, e)
        raise


def put_file(key: str, fileobj, content_type: str, metadata: dict | None = None) -> str | None:
    s3 = get_s3_client()
    extra = {"ContentType": content_type}
    if metadata:
        extra["Metadata"] = metadata
    try:
        s3.upload_fileobj(
            Fileobj=fileobj,
            Bucket=settings.S3_BUCKET,
            Key=key,
            ExtraArgs=extra,
        )
        return None
    except (ClientError, BotoCoreError) as e:
        logger.exception("S3 put_file failed (key=%s): %s", key, e)
        raise ValueError("DOC_S3_ERROR")


def delete_file(key: str) -> None:
    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
    except ClientError as e:
        code = (e.response or {}).get("Error", {}).get("Code")
        if code in {"NoSuchKey", "NotFound"}:
            return
        raise ValueError("DOC_S3_ERROR")
    except BotoCoreError:
        raise ValueError("DOC_S3_ERROR")
