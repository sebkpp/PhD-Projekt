from starlette import status


def test_create_study(client):
    resp = client.post("/studies/", json={"status": "Aktiv"})
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "study_id" in data
    assert data["study_id"] is not None


def test_list_studies(client):
    client.post("/studies/", json={"status": "Aktiv"})
    resp = client.get("/studies/")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_study_by_id(client, study_id):
    resp = client.get(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["study_id"] == study_id


def test_get_study_not_found(client):
    resp = client.get("/studies/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_study(client, study_id):
    resp = client.put(f"/studies/{study_id}", json={"status": "Beendet"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "Beendet"


def test_delete_study(client, study_id):
    resp = client.delete(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_delete_study_not_found(client):
    resp = client.delete("/studies/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_experiments_by_study(client, study_id, experiment_id):
    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
    assert any(e["experiment_id"] == experiment_id for e in data)


def test_close_study(client, study_id):
    resp = client.post(f"/studies/{study_id}/close")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["ended_at"] is not None
