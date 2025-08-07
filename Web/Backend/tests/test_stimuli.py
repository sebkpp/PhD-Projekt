import pytest
from Backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_stimuli_success(client):
    response = client.get('/api/stimuli')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "type" in first
    assert first["type"] in ("visual", "auditory", "tactile")

def test_get_stimuli_empty(monkeypatch, client):
    def mock_empty(session):
        return []

    monkeypatch.setattr('Backend.routes.stimuli.get_all_stimuli', mock_empty)

    response = client.get('/api/stimuli')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

import Backend.routes.stimuli
def test_get_stimuli_internal_error(monkeypatch, client):

    def mock_error(_):
        raise Exception("Fehler beim Laden der Stimuli")

    monkeypatch.setattr(Backend.routes.stimuli, "get_all_stimuli", mock_error)

    response = client.get('/api/stimuli')
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data

def test_stimuli_contains_all_types(client):
    response = client.get('/api/stimuli')
    assert response.status_code == 200

    data = response.get_json()
    types = {item["type"] for item in data}

    assert {"visual", "auditory", "tactile"}.issubset(types)

def test_stimuli_names_not_empty(client):
    response = client.get('/api/stimuli')
    assert response.status_code == 200

    data = response.get_json()
    for item in data:
        assert "name" in item
        assert isinstance(item["name"], str)
        assert len(item["name"]) > 0

def test_stimuli_no_unknown_types(client):
    response = client.get('/api/stimuli')
    assert response.status_code == 200

    data = response.get_json()
    valid_types = {"visual", "auditory", "tactile"}
    for item in data:
        assert item["type"] in valid_types

def test_stimuli_ids_unique(client):
    response = client.get('/api/stimuli')
    assert response.status_code == 200

    data = response.get_json()
    ids = [item["id"] for item in data]
    assert len(ids) == len(set(ids))

def test_stimuli_content_type(client):
    response = client.get('/api/stimuli')
    assert response.headers['Content-Type'].startswith('application/json')