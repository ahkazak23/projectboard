import pytest

from app.schemas import ProjectIn, ProjectUpdate
from app.services import project as svc


def test_non_member_get_forbidden(db_session, user_factory):
    owner = user_factory("pown", "pw")
    stranger = user_factory("str", "pw")
    p = svc.create_project(db_session, owner, ProjectIn(name="X", description="d"))
    with pytest.raises(PermissionError) as e:
        svc.get_project(db_session, stranger, p.id)
    assert "FORBIDDEN" in str(e.value)


def test_unknown_project_not_found(db_session, user_factory):
    u = user_factory("u1", "pw")
    with pytest.raises(ValueError) as e:
        svc.get_project(db_session, u, 999_999)
    assert "NOT_FOUND" in str(e.value)


def test_delete_by_participant_forbidden(db_session, user_factory):
    owner = user_factory("own_del", "pw")
    part = user_factory("part_del", "pw")
    p = svc.create_project(db_session, owner, ProjectIn(name="Del", description="d"))
    svc.invite_user(db_session, owner, p.id, part.login)
    with pytest.raises(PermissionError) as e:
        svc.delete_project(db_session, part, p.id)
    assert "FORBIDDEN" in str(e.value)


def test_owner_delete_ok_then_not_found(db_session, user_factory):
    owner = user_factory("own_del2", "pw")
    p = svc.create_project(db_session, owner, ProjectIn(name="ToDel", description="d"))
    svc.delete_project(db_session, owner, p.id)
    with pytest.raises(ValueError) as e:
        svc.get_project(db_session, owner, p.id)
    assert "NOT_FOUND" in str(e.value)


def test_invite_unknown_user_404(db_session, user_factory):
    owner = user_factory("own_inv", "pw")
    p = svc.create_project(db_session, owner, ProjectIn(name="Inv", description="d"))
    with pytest.raises(ValueError) as e:
        svc.invite_user(db_session, owner, p.id, "no_such_login")
    assert "TARGET_NOT_FOUND" in str(e.value)


def test_invite_idempotent(db_session, user_factory):
    owner = user_factory("own_idem", "pw")
    part = user_factory("part_idem", "pw")
    p = svc.create_project(db_session, owner, ProjectIn(name="Idem", description="d"))
    svc.invite_user(db_session, owner, p.id, part.login)
    svc.invite_user(db_session, owner, p.id, part.login)

    upd = svc.update_project(db_session, part, p.id, ProjectUpdate(description="ok"))
    assert upd.description == "ok"
