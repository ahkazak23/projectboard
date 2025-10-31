from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.db.models import User
from app.schemas import ProjectIn, ProjectOut, ProjectUpdate
from app.services import project as project_svc

router = APIRouter(tags=["projects"])


@router.post(
    "/projects",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
def create_project_endpoint(
    data: ProjectIn,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = project_svc.create_project(db, current_user, data)
    if response is not None:
        response.headers["Location"] = f"/project/{proj.id}/info"
    return proj


@router.get("/projects", response_model=list[ProjectOut], summary="List accessible projects")
def list_projects_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_svc.list_projects(db, current_user)


@router.get(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    summary="Get project details",
)
def get_project_endpoint(
    project_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_svc.get_project(db, current_user, project_id)


@router.put(
    "/project/{project_id}/info",
    response_model=ProjectOut,
    summary="Update project details",
)
def update_project_endpoint(
    data: ProjectUpdate,
    project_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_svc.update_project(db, current_user, project_id, data)


@router.delete(
    "/project/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project (owner only)",
)
def delete_project_endpoint(
    project_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_svc.delete_project(db, current_user, project_id)


@router.post(
    "/project/{project_id}/invite",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Invite user by login",
)
def invite_user_endpoint(
    project_id: int = Path(..., ge=1),
    target_login: str = Query(..., min_length=1, alias="user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_svc.invite_user(db, current_user, project_id, target_login)
