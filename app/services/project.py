from sqlalchemy import select, exists, func, literal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.models import Project, ProjectAccess, ProjectRole, User
from app.schemas import ProjectIn, ProjectUpdate


def create_project(db: Session, current_user: User, data: ProjectIn) -> Project:
    proj = Project(
        name=data.name,
        description=data.description,
        owner_id=current_user.id
    )
    db.add(proj)
    db.flush()

    owner_link = ProjectAccess(
        project_id=proj.id,
        user_id=current_user.id,
        role=ProjectRole.owner,
    )
    db.add(owner_link)

    db.commit()
    db.refresh(proj)
    return proj


def list_projects(db: Session, current_user: User) -> list[Project]:
    stmt = (
        select(Project)
        .join(ProjectAccess, ProjectAccess.project_id == Project.id)
        .where(ProjectAccess.user_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_project(db: Session, current_user: User, project_id: int) -> Project:
    proj = _get_project_or_404(db, project_id)
    _ensure_member(db, current_user.id, project_id)
    return proj


def update_project(db: Session, current_user: User, project_id: int, data: ProjectUpdate) -> Project:
    proj = _get_project_or_404(db, project_id)
    _ensure_member(db, current_user.id, project_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(proj, field, value)

    db.commit()
    db.refresh(proj)
    return proj


def delete_project(db: Session, current_user: User, project_id: int) -> None:
    proj = _get_project_or_404(db, project_id)
    _ensure_owner(current_user.id, proj)

    db.delete(proj)
    db.commit()
    return None


def invite_user(db: Session, owner_user: User, project_id: int, target_login: str) -> None:
    proj = _get_project_or_404(db, project_id)
    _ensure_owner(owner_user.id, proj)

    target = (
        db.query(User)
        .filter(func.lower(User.login) == target_login.lower())
        .one_or_none()
    )
    if target is None:
        raise ValueError("TARGET_NOT_FOUND")

    if _is_member(db, target.id, project_id):
        return None

    access = ProjectAccess(
        project_id=proj.id,
        user_id=target.id,
        role=ProjectRole.participant,
    )
    db.add(access)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    return None



# Private helpers
def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise ValueError("NOT_FOUND")
    return project


def _is_owner(user_id: int, project: Project) -> bool:
    return project.owner_id == user_id


def _ensure_owner(user_id: int, project: Project) -> None:
    if not _is_owner(user_id, project):
        raise PermissionError("FORBIDDEN")


def _is_member(db: Session, user_id: int, project_id: int) -> bool:
    stmt = select(
        exists().where(
            (ProjectAccess.user_id == user_id) &
            (ProjectAccess.project_id == project_id)
        )
    )
    return db.scalar(stmt) is True


def _ensure_member(db: Session, user_id: int, project_id: int) -> None:
    if not _is_member(db, user_id, project_id):
        raise PermissionError("FORBIDDEN")
