from fastapi import (APIRouter, Depends,
                     Query, Path, status, HTTPException,
                     Response)
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas import ProjectIn, ProjectUpdate, ProjectOut
from app.db.models import User
from app.services import project as project_svc


def _translate_service_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    if isinstance(exc, ValueError):
        msg = str(exc)
        if msg == "NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        if msg == "TARGET_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    raise


router = APIRouter(tags=["projects"])


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED, summary="Create project")
def create_project_endpoint(
        data: ProjectIn,
        response: Response,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        proj = project_svc.create_project(db, current_user, data)
        if response is not None:
            response.headers["Location"] = f"/project/{proj.id}/info"
        return proj
    except Exception as exc:
        _translate_service_error(exc)


@router.get("/projects", response_model=list[ProjectOut], summary="List accessible projects")
def list_projects_endpoint(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        return project_svc.list_projects(db, current_user)
    except Exception as exc:
        _translate_service_error(exc)


@router.get("/project/{project_id}/info", response_model=ProjectOut, summary="Get project details")
def get_project_endpoint(
        project_id: int = Path(..., ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        return project_svc.get_project(db, current_user, project_id)
    except Exception as exc:
        _translate_service_error(exc)


@router.put("/project/{project_id}/info", response_model=ProjectOut, summary="Update project details")
def update_project_endpoint(
        data: ProjectUpdate,
        project_id: int = Path(..., ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        return project_svc.update_project(db, current_user, project_id, data)
    except Exception as exc:
        _translate_service_error(exc)


@router.delete("/project/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete project (owner only)")
def delete_project_endpoint(
        project_id: int = Path(..., ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    try:
        return project_svc.delete_project(db, current_user, project_id)
    except Exception as exc:
        _translate_service_error(exc)


@router.post("/project/{project_id}/invite", status_code=status.HTTP_204_NO_CONTENT, summary="Invite user by login")
def invite_user_endpoint(
        project_id: int = Path(..., ge=1),
        target_login: str = Query(..., min_length=1, alias="user"),
        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        return project_svc.invite_user(db, current_user, project_id, target_login)
    except Exception as exc:
        _translate_service_error(exc)
