from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),server_default=func.now())

    # relationship
    owner = relationship(
        "User",
        back_populates="owned_projects",
        lazy="joined"
    )
    access_list = relationship(
        "ProjectAccess",
        back_populates="project",
        cascade="all, delete-orphan",
    )