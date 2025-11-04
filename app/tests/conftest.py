import os
import tempfile
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.services import auth as auth_svc


@pytest.fixture(scope="session")
def engine():
    fd, path = tempfile.mkstemp(prefix="testdb_", suffix=".sqlite")
    os.close(fd)
    url = f"sqlite:///{path}"
    eng = create_engine(url, future=True, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    try:
        yield eng
    finally:
        eng.dispose()
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_factory(db_session):
    def _create(login: str, password: str = "pass"):
        unique_login = f"{login}_{uuid4().hex[:6]}"
        return auth_svc.register(db_session, login=unique_login, password=password)
    return _create



@pytest.fixture
def token_factory(db_session):
    def _make(login: str, password: str = "pass"):
        token, expires_in = auth_svc.login(db_session, login=login, password=password)
        return token, expires_in

    return _make
