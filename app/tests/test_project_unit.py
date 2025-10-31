from app.db.models import ProjectAccess, ProjectRole
from app.schemas import ProjectIn, ProjectUpdate
from app.services import project as svc


def test_create_project_sets_owner_and_access(db_session, user_factory):
    owner = user_factory("owner", "pw")
    data = {"name": "Proj1", "description": "desc"}
    p = svc.create_project(db_session, owner, ProjectIn(**data))
    assert p.id is not None
    assert p.owner_id == owner.id
    link = db_session.query(ProjectAccess).filter_by(project_id=p.id, user_id=owner.id).one()
    assert link.role == ProjectRole.owner


def test_list_projects_returns_only_user_projects(db_session, user_factory):
    owner = user_factory("own", "pw")
    user2 = user_factory("part", "pw")
    data = {"name": "A", "description": ""}
    p1 = svc.create_project(db_session, owner, ProjectIn(**data))
    svc.invite_user(db_session, owner, p1.id, user2.login)
    owned = svc.list_projects(db_session, owner)
    part = svc.list_projects(db_session, user2)
    assert p1.id in [x.id for x in owned]
    assert p1.id in [x.id for x in part]


def test_update_project_changes_fields(db_session, user_factory):
    owner = user_factory("own2", "pw")
    data = {"name": "Old", "description": "d"}
    p = svc.create_project(db_session, owner, ProjectIn(**data))
    upd_data = {"description": "New"}
    upd = svc.update_project(db_session, owner, p.id, ProjectUpdate(**upd_data))
    assert upd.description == "New"


def test_invite_user_adds_participant(db_session, user_factory):
    owner = user_factory("boss", "pw")
    invited = user_factory("friend", "pw")
    data = {"name": "Demo", "description": ""}
    p = svc.create_project(db_session, owner, ProjectIn(**data))
    svc.invite_user(db_session, owner, p.id, invited.login)
    links = db_session.query(ProjectAccess).filter_by(user_id=invited.id, project_id=p.id).all()
    assert len(links) == 1
    assert links[0].role == ProjectRole.participant
