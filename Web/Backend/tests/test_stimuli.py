from starlette import status


def test_list_stimuli(client):
    resp = client.get("/stimuli/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)


def test_get_stimuli_response_structure(client):
    """GET /stimuli/ → jedes Element enthält stimuli_type_id und type_name."""
    resp = client.get("/stimuli/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert "stimuli_type_id" in item
        assert "type_name" in item
