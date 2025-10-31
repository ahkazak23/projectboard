from __future__ import annotations

import datetime as dt

import pytest

from app.db.models.project import Project
from app.db.models.project_access import ProjectAccess
from app.db.models.document import Document
from app.services import document as doc_svc


# helpers
def _mk_project(db, owner_id: int, name="p1", desc="d1") -> Project:
    p = Project(name=name, description=desc, owner_id=owner_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _add_participant(db, project_id: int, user_id: int) -> None:
    db.add(ProjectAccess(project_id=project_id, user_id=user_id, role="participant"))
    db.commit()


def _mk_doc(db, project_id: int, filename: str, size: int = 10, uploaded_by: int | None = None) -> Document:
    d = Document(
        project_id=project_id,
        filename=filename,
        s3_key=f"projects/{project_id}/{filename}",
        size_bytes=size,
        uploaded_by=uploaded_by,
        uploaded_at=dt.datetime.utcnow(),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# tests: list
def test_list_documents_owner_sees_all(db_session, user_factory):
    owner = user_factory("owner1")
    p = _mk_project(db_session, owner.id)
    d1 = _mk_doc(db_session, p.id, "a.pdf")
    d2 = _mk_doc(db_session, p.id, "b.pdf")

    out = doc_svc.list_documents(
        db_session, user_id=owner.id, project_id=p.id, page=1, page_size=50
    )

    assert out["total"] == 2
    names = [x.filename for x in out["items"]]
    # order by uploaded_at desc
    assert names == [d2.filename, d1.filename]


def test_list_documents_participant_sees_all(db_session, user_factory):
    owner = user_factory("owner2")
    user = user_factory("user2")
    p = _mk_project(db_session, owner.id)
    _add_participant(db_session, p.id, user.id)
    _mk_doc(db_session, p.id, "r1.txt")
    _mk_doc(db_session, p.id, "r2.txt")

    out = doc_svc.list_documents(
        db_session, user_id=user.id, project_id=p.id, page=1, page_size=10
    )
    assert out["total"] == 2
    assert len(out["items"]) == 2


def test_list_documents_non_member_forbidden(db_session, user_factory):
    owner = user_factory("owner3")
    alien = user_factory("alien3")
    p = _mk_project(db_session, owner.id)
    _mk_doc(db_session, p.id, "secret.pdf")

    with pytest.raises(ValueError):  # DOC_NO_ACCESS from _ensure_access
        doc_svc.list_documents(db_session, user_id=alien.id, project_id=p.id)


def test_list_documents_pagination_and_search(db_session, user_factory):
    owner = user_factory("owner4")
    p = _mk_project(db_session, owner.id)
    _mk_doc(db_session, p.id, "report-q1.pdf")
    _mk_doc(db_session, p.id, "report-q2.pdf")
    _mk_doc(db_session, p.id, "notes.txt")

    out = doc_svc.list_documents(
        db_session, user_id=owner.id, project_id=p.id, page=1, page_size=1, q="report"
    )
    assert out["total"] == 2
    assert len(out["items"]) == 1  # page_size=1
    # page 2
    out2 = doc_svc.list_documents(
        db_session, user_id=owner.id, project_id=p.id, page=2, page_size=1, q="report"
    )
    assert len(out2["items"]) == 1
    assert out["items"][0].id != out2["items"][0].id


# tests: presigned link
def test_presigned_link_happy_path(db_session, user_factory, monkeypatch):
    owner = user_factory("owner5")
    p = _mk_project(db_session, owner.id)
    d = _mk_doc(db_session, p.id, "file.pdf")

    def fake_presign(*, key: str, ttl: int = 600, **kwargs) -> str:
        assert key == d.s3_key
        assert 1 <= ttl <= 3600
        return f"https://example.com/{key}?X-Amz-Signature=fake&X-Amz-Expires={ttl}"

    monkeypatch.setattr(doc_svc, "presigned_download_url", fake_presign, raising=True)

    out = doc_svc.get_document_download_link_by_id(
        db_session, user_id=owner.id, doc_id=d.id, ttl=700
    )
    assert "url" in out and out["url"].startswith("https://example.com/")
    assert out["expires_in"] == 700



def test_presigned_link_wrong_project_404(db_session, user_factory, monkeypatch):
    owner = user_factory("owner6")
    other = user_factory("owner6b")
    p2 = _mk_project(db_session, other.id)
    d = _mk_doc(db_session, p2.id, "other.pdf")

    with pytest.raises(ValueError):
        doc_svc.get_document_download_link_by_id(
            db_session, user_id=owner.id, doc_id=d.id
        )



def test_presigned_link_forbidden_non_member(db_session, user_factory):
    owner = user_factory("owner7")
    alien = user_factory("alien7")
    p = _mk_project(db_session, owner.id)
    d = _mk_doc(db_session, p.id, "private.pdf")

    with pytest.raises(ValueError):
        doc_svc.get_document_download_link_by_id(
            db_session, user_id=alien.id, doc_id=d.id
        )