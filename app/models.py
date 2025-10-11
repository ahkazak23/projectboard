from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)