from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.db.models.project import Project
    from app.db.models.user import User
import enum
from sqlalchemy import Enum as SAEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProjectRole(enum.Enum):
    owner = "owner"
    participant = "participant"


class ProjectAccess(Base):
    __tablename__ = "project_access"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[ProjectRole] = mapped_column(
        SAEnum(ProjectRole, name="project_role"), nullable=False
    )

    # relationships
    project: Mapped["Project"] = relationship(back_populates="access_list")
    user: Mapped["User"] = relationship(back_populates="project_links")

    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)