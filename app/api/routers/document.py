from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from sqlalchemy.orm import Session
from starlette import status

from app.core.deps import get_current_user
from app.core.storage_s3 import ping_bucket
from app.db.models import User
from app.db.session import get_db
from app.schemas.document import (
    DocumentDownloadLinkOut,
    DocumentListOut,
    DocumentOut,
)
from app.services.document import (
    delete_document_by_id,
    get_document_download_link_by_id,
    list_documents,
    replace_document,
    upload_document,
)

proj_router = APIRouter(prefix="/projects", tags=["documents"])
doc_router = APIRouter(prefix="/document", tags=["documents"])


# proj_router
@proj_router.post(
    "/{project_id}/documents",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
def upload_project_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return upload_document(
        db,
        user_id=current_user.id,
        project_id=project_id,
        file=file,
    )


@proj_router.get(
    "/{project_id}/documents",
    response_model=DocumentListOut,
    summary="List documents in a project",
)
def list_project_documents(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: str | None = Query(None, description="Filter by filename (ILIKE)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_documents(
        db,
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        page_size=page_size,
        q=q,
    )


# doc_router
@doc_router.get(
    "/{doc_id}",
    response_model=DocumentDownloadLinkOut,
    summary="Get presigned download link for a document",
    description="Returns a short-lived S3 presigned GET URL (not a file stream).",
)
def get_document_link_by_id(
    doc_id: int = Path(..., ge=1),
    ttl: int = Query(600, ge=1, le=3600, description="Seconds (default 600, max 3600)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_document_download_link_by_id(
        db=db,
        user_id=current_user.id,
        doc_id=doc_id,
        ttl=ttl,
    )


@doc_router.put(
    "/{doc_id}",
    response_model=DocumentOut,
    status_code=status.HTTP_200_OK,
    summary="Replace a document file and metadata",
    description="Uploads a new file, swaps metadata, updates project total size; old file deleted.",
)
def replace_document_endpoint(
    doc_id: int = Path(..., ge=1),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return replace_document(
        db=db,
        user_id=current_user.id,
        doc_id=doc_id,
        file=file,
    )


@doc_router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Owner-only per project rules. Removes DB record and S3 object.",
)
def delete_document_by_id_endpoint(
    doc_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_document_by_id(
        db=db,
        user_id=current_user.id,
        doc_id=doc_id,
    )
    return


# Dev ping
@doc_router.get("/ping")
def s3_ping(current_user: User = Depends(get_current_user)):
    ok = ping_bucket()
    return {"ok": ok}
