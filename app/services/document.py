from __future__ import annotations

import io
import re
from typing import BinaryIO
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage_s3 import delete_file, put_file
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

    # S3 upload
    buf: BinaryIO = io.BytesIO(blob)
    put_file(key, buf, ctype, metadata={"original": file.filename or ""})

    # DB save
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

    db.commit()
    db.refresh(doc)
    return doc


def delete_document(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    doc_id: int,
) -> None:
    doc = _get_doc_or_404(db, project_id, doc_id)
    proj = _get_project_or_404(db, project_id)
    _ensure_owner(user_id, proj)

    # S3 delete
    delete_file(doc.s3_key)

    # total_size_bytes decrement (never negative)
    _decrement_total_size(proj, doc.size_bytes)

    # DB delete
    db.delete(doc)
    db.commit()


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
