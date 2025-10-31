from __future__ import annotations

import io
import re
from datetime import datetime
from typing import BinaryIO, Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage_s3 import delete_file, put_file, presigned_download_url
from app.db.models.document import Document
from app.db.models.project import Project
from app.db.models.project_access import ProjectAccess

# Config
ALLOWED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
    "text/plain",
}

MAX_UPLOAD_BYTES = settings.PROJECT_SIZE_LIMIT_BYTES


def upload_document(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    file: UploadFile,
) -> Document:
    proj = _ensure_access(db, user_id, project_id)

    ctype = (file.content_type or "").lower()
    if ctype not in ALLOWED_MIME:
        raise ValueError("DOC_UNSUPPORTED_TYPE")

    blob = _read_limited(file, MAX_UPLOAD_BYTES)
    size = len(blob)

    limit = settings.PROJECT_SIZE_LIMIT_BYTES
    current = getattr(proj, "total_size_bytes", 0) or 0
    if current + size > limit:
        raise ValueError("DOC_PROJECT_LIMIT")

    safe = _sanitize_filename(file.filename or "file")
    key = f"projects/{project_id}/{uuid4()}-{safe}"

    try:
        buf: BinaryIO = io.BytesIO(blob)
        put_file(key, buf, ctype, metadata={"original": file.filename or ""})
    except Exception:
        raise

    try:
        with db.begin():
            doc = Document(
                project_id=project_id,
                filename=file.filename or safe,
                s3_key=key,
                size_bytes=size,
                uploaded_by=user_id,
            )
            db.add(doc)

            if hasattr(Project, "total_size_bytes"):
                current = getattr(proj, "total_size_bytes", 0) or 0
                setattr(proj, "total_size_bytes", current + size)

        db.refresh(doc)
        return doc

    except Exception as db_err:
        delete_file(key)
        raise db_err


def list_documents(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    page: int = 1,
    page_size: int = 50,
    q: Optional[str] = None,
) -> dict:
    _ensure_access(db, user_id, project_id)

    page = max(1, page or 1)
    page_size = max(1, min(page_size or 50, 200))

    qry = db.query(Document).filter(Document.project_id == project_id)
    cnt = db.query(func.count(Document.id)).filter(Document.project_id == project_id)

    if q:
        like = f"%{q}%"
        qry = qry.filter(Document.filename.ilike(like))
        cnt = cnt.filter(Document.filename.ilike(like))

    qry = qry.order_by(Document.uploaded_at.desc())
    items = qry.offset((page - 1) * page_size).limit(page_size).all()
    total = cnt.scalar() or 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_document_download_link_by_id(
    db: Session,
    *,
    user_id: int,
    doc_id: int,
    ttl: int = 600,
) -> dict:
    doc = db.get(Document, doc_id)
    if not doc:
        raise ValueError("DOC_NOT_FOUND")

    _ensure_access(db, user_id, doc.project_id)

    url = presigned_download_url(key=doc.s3_key, ttl=ttl)
    expires_in = min(max(ttl, 1), 3600)
    return {"url": url, "expires_in": expires_in}


def replace_document(
    db: Session,
    *,
    user_id: int,
    doc_id: int,
    file: UploadFile,
) -> Document:
    doc = db.get(Document, doc_id)
    if not doc:
        raise ValueError("DOC_NOT_FOUND")
    proj = _get_project_or_404(db, doc.project_id)

    _ensure_access(db, user_id, proj.id)

    ctype = (file.content_type or "").lower()
    if ctype not in ALLOWED_MIME:
        raise ValueError("DOC_UNSUPPORTED_TYPE")

    blob = _read_limited(file, MAX_UPLOAD_BYTES)
    new_size = len(blob)
    old_size = doc.size_bytes or 0

    limit = settings.PROJECT_SIZE_LIMIT_BYTES
    current_total = getattr(proj, "total_size_bytes", 0) or 0
    projected_total = current_total - old_size + new_size
    if projected_total > limit:
        raise ValueError("DOC_PROJECT_LIMIT")

    safe = _sanitize_filename(file.filename or "file")
    new_key = f"projects/{proj.id}/{uuid4()}-{safe}"
    old_key = doc.s3_key

    try:
        buf: BinaryIO = io.BytesIO(blob)
        put_file(new_key, buf, ctype, metadata={"original": file.filename or ""})
    except Exception:
        raise

    try:
        txn_ctx = db.begin_nested() if db.in_transaction() else db.begin()
        with txn_ctx:
            doc.s3_key = new_key
            doc.filename = file.filename or safe
            doc.size_bytes = new_size
            doc.uploaded_by = user_id
            doc.uploaded_at = datetime.utcnow()

            if hasattr(Project, "total_size_bytes"):
                proj.total_size_bytes = max(projected_total, 0)

        if old_key and old_key != new_key:
            try:
                delete_file(old_key)
            except Exception:
                pass

        db.refresh(doc)
        return doc

    except Exception as db_err:
        try:
            delete_file(new_key)
        except Exception:
            pass
        raise db_err


def delete_document_by_id(
    db: Session,
    *,
    user_id: int,
    doc_id: int,
) -> None:
    doc = db.get(Document, doc_id)
    if not doc:
        raise ValueError("DOC_NOT_FOUND")

    proj = _get_project_or_404(db, doc.project_id)
    _ensure_owner(user_id, proj)

    try:
        delete_file(doc.s3_key)
    except Exception:
        raise

    try:
        with db.begin():
            _decrement_total_size(proj, doc.size_bytes)
            db.delete(doc)
    except Exception:
        raise


# Private Helpers
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]")


def _sanitize_filename(name: str) -> str:
    name = (name or "file").strip().replace(" ", "_")
    return _SAFE_NAME_RE.sub("", name)


def _ensure_access(db: Session, user_id: int, project_id: int) -> Project:
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise ValueError("NOT_FOUND")
    if proj.owner_id == user_id:
        return proj
    has = (
        db.query(ProjectAccess)
        .filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id,
        )
        .first()
    )
    if not has:
        raise ValueError("DOC_NO_ACCESS")
    return proj


def _read_limited(upload: UploadFile, max_bytes: int) -> bytes:
    data = upload.file.read(max_bytes + 1)
    if len(data) == 0:
        raise ValueError("DOC_EMPTY")
    if len(data) > max_bytes:
        raise ValueError("DOC_TOO_LARGE")
    return data


def _get_project_or_404(db: Session, project_id: int) -> Project:
    proj = db.get(Project, project_id)
    if not proj:
        raise ValueError("NOT_FOUND")
    return proj


def _ensure_owner(user_id: int, proj: Project) -> None:
    if proj.owner_id != user_id:
        raise ValueError("DOC_NO_ACCESS")


def _get_doc_or_404(db: Session, project_id: int, doc_id: int) -> Document:
    doc = db.get(Document, doc_id)
    if not doc or doc.project_id != project_id:
        raise ValueError("DOC_NOT_FOUND")
    return doc


def _decrement_total_size(proj: Project, delta: int | None) -> None:
    if hasattr(Project, "total_size_bytes") and delta:
        cur = getattr(proj, "total_size_bytes", 0) or 0
        proj.total_size_bytes = max(cur - max(delta, 0), 0)