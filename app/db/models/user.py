from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # relationships
    owned_projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    project_links = relationship(
        "ProjectAccess",
        back_populates="user",
        cascade="all, delete-orphan",
    )