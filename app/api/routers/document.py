from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, Query, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.deps import get_current_user
from app.core.storage_s3 import ping_bucket
from app.db.models import User
from app.db.session import get_db
from app.schemas.document import DocumentOut, DocumentListOut, DocumentDownloadLinkOut
from app.services.document import delete_document, upload_document, list_documents, get_document_download_link

router = APIRouter(prefix="/projects", tags=["documents"])


@router.post(
    "/{project_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED
)
def upload_project_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    doc = upload_document(
        db,
        user_id=current_user.id,
        project_id=project_id,
        file=file,
    )
    return doc


@router.delete("/{project_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_document(
    project_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_document(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        doc_id=doc_id,
    )
    return

@router.get(
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
    data = list_documents(
        db,
        user_id=current_user.id,
        project_id=project_id,
        page=page,
        page_size=page_size,
        q=q,
    )
    return data

@router.get(
    "/{project_id}/documents/{doc_id}",
    response_model=DocumentDownloadLinkOut,
    summary="Get presigned download link",
    description="Returns a short-lived S3 presigned **GET** URL for direct download.",
)
def get_project_document_download_link(
    project_id: int = Path(..., ge=1),
    doc_id: int = Path(..., ge=1),
    ttl: int = Query(600, ge=1, le=3600, description="Seconds (default 600, max 3600)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = get_document_download_link(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        doc_id=doc_id,
        ttl=ttl,
    )
    return data


@router.get("/ping")
def s3_ping():
    ok = ping_bucket()
    return {"ok": ok}
