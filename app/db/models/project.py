from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.project_access import ProjectAccess
    from app.db.models.document import Document
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    # relationships
    owner: Mapped["User"] = relationship(
        back_populates="owned_projects",
        lazy="joined",
    )
    access_list: Mapped[list["ProjectAccess"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r}>"