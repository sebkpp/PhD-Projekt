from starlette import status


def test_list_stimuli(client):
    resp = client.get("/stimuli/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
