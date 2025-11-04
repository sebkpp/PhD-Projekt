# import pytest
# from Backend.app import app
#
# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#
# def test_get_avatar_visibility_success(client):
#     response = client.get('/api/avatar-visibility')
#     assert response.status_code == 200
#
#     data = response.get_json()
#     assert isinstance(data, list)
#     assert len(data) > 0
#
#     first = data[0]
#     assert "id" in first
#     assert "name" in first
#     assert "label" in first
#
#     expected_labels = {"Nur Hände", "Kopf + Hände", "Ganze Figur"}
#     assert first["label"] in expected_labels
#
# def test_get_avatar_visibility_empty(monkeypatch, client):
#     def mock_empty():
#         return []
#
#     monkeypatch.setattr('Backend.routes.avatar_visibility.get_all_avatar_visibility', mock_empty)
#
#     response = client.get('/api/avatar-visibility')
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data == []
#
# def test_get_avatar_visibility_internal_error(monkeypatch, client):
#     def mock_error():
#         raise Exception("Test Exception")
#
#     monkeypatch.setattr('Backend.routes.avatar_visibility.get_all_avatar_visibility', mock_error)
#
#     response = client.get('/api/avatar-visibility')
#     assert response.status_code == 500
#     data = response.get_json()
#     assert "error" in data
#
# def test_get_avatar_visibility_all_entries(client):
#     response = client.get('/api/avatar-visibility')
#     assert response.status_code == 200
#
#     data = response.get_json()
#     expected_names = {"hands", "head", "full"}
#     expected_labels = {"Nur Hände", "Kopf + Hände", "Ganze Figur"}
#
#     returned_names = {item['name'] for item in data}
#     returned_labels = {item['label'] for item in data}
#
#     assert expected_names == returned_names
#     assert expected_labels == returned_labels
#
# def test_avatar_visibility_content_type(client):
#     response = client.get('/api/avatar-visibility')
#     assert response.headers['Content-Type'].startswith('application/json')
#
# def test_avatar_visibility_no_extra_fields(client):
#     response = client.get('/api/avatar-visibility')
#     data = response.get_json()
#
#     allowed_keys = {"id", "name", "label"}
#     for item in data:
#         assert set(item.keys()) <= allowed_keys
#
# def test_avatar_visibility_empty(monkeypatch, client):
#     def mock_empty():
#         return []
#
#     monkeypatch.setattr('Backend.routes.avatar_visibility.get_all_avatar_visibility', mock_empty)
#     response = client.get('/api/avatar-visibility')
#     assert response.status_code == 200
#     assert response.get_json() == []