import enum

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class ProjectRole(enum.Enum):
    owner = "owner"
    participant = "participant"


class ProjectAccess(Base):
    __tablename__ = "project_access"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(SAEnum(ProjectRole, name="project_role"), nullable=False)

    # relationships
    project = relationship("Project", back_populates="access_list")
    user = relationship("User", back_populates="project_links")

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )
