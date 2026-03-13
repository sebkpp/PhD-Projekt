import pytest
from starlette import status
from Backend.models.avatar_visibility import AvatarVisibility
from Backend.db_session import SessionLocal


@pytest.fixture
def seeded_avatar_visibility():
    """Fügt zwei AvatarVisibility-Einträge in die Test-DB ein und räumt danach auf."""
    db = SessionLocal()
    # Vorhandene Einträge mit denselben Namen entfernen (UNIQUE-Constraint)
    db.query(AvatarVisibility).filter(
        AvatarVisibility.avatar_visibility_name.in_(["full", "none"])
    ).delete(synchronize_session=False)
    db.commit()

    entries = [
        AvatarVisibility(avatar_visibility_name="full", label="Vollständig sichtbar"),
        AvatarVisibility(avatar_visibility_name="none", label="Unsichtbar"),
    ]
    db.add_all(entries)
    db.commit()
    ids = [e.avatar_visibility_id for e in entries]
    db.close()

    yield ids

    db = SessionLocal()
    db.query(AvatarVisibility).filter(
        AvatarVisibility.avatar_visibility_name.in_(["full", "none"])
    ).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_list_avatar_visibility_empty(client):
    """Leere Tabelle liefert 200 mit leerer Liste – kein 404."""
    db = SessionLocal()
    db.query(AvatarVisibility).delete()
    db.commit()
    db.close()

    resp = client.get("/avatar-visibility/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []


def test_list_avatar_visibility_returns_correct_fields(client, seeded_avatar_visibility):
    """Antwort enthält die Felder id, name, label – nicht avatar_id oder visible."""
    resp = client.get("/avatar-visibility/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "label" in item
        assert "avatar_id" not in item
        assert "visible" not in item


def test_list_avatar_visibility_values(client, seeded_avatar_visibility):
    """Datenwerte stimmen mit den geseedeten Einträgen überein."""
    resp = client.get("/avatar-visibility/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    names = {item["name"] for item in data}
    labels = {item["label"] for item in data}
    assert "full" in names
    assert "none" in names
    assert "Vollständig sichtbar" in labels
    assert "Unsichtbar" in labels
