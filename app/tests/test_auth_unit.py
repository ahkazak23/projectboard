import pytest
from app.core.errors import AuthError, UserExistsError
from app.services import auth as auth_svc
from app.db.models import User


def test_register_creates_user_and_normalizes_login(db_session):
    u = auth_svc.register(db_session, login="  Alice  ", password="secret")
    assert isinstance(u, User)
    assert u.id is not None
    assert u.login == "alice"


def test_login_success_returns_token_and_expires_in(db_session, user_factory):
    user_factory("owner1", "secret")
    token, expires_in = auth_svc.login(db_session, login="OWNER1", password="secret")
    assert isinstance(token, str) and len(token) > 10
    assert isinstance(expires_in, int) and expires_in > 0


def test_login_wrong_password_raises_autherror(db_session, user_factory):
    user_factory("alice_wrongcase", "secret")
    with pytest.raises(AuthError):
        auth_svc.login(db_session, login="alice_wrongcase", password="wrong")


def test_register_duplicate_raises_userexistserror(db_session):
    auth_svc.register(db_session, login="Bob", password="x")
    with pytest.raises(UserExistsError):
        auth_svc.register(db_session, login="  bob  ", password="x")
