from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File

from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.deps import get_current_user
from app.core.storage_s3 import ping_bucket
from app.db.models import User
from app.db.session import get_db
from app.schemas.document import DocumentOut
from app.services.document import upload_document

router = APIRouter(prefix="/projects", tags=["documents"])

@router.post("/{project_id}/documents",response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
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
        user=current_user,
        project_id=project_id,
        file=file,
    )
    return doc


@router.get("/ping")
def s3_ping():
    ok = ping_bucket()
    return {"ok": ok}