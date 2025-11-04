# import pytest
# from Backend.app import app
# import json
#
# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#
# def test_register_participant_success(client):
#     payload = {
#         "age": 28,
#         "gender": "male",
#         "handedness": "right"
#     }
#     res = client.post('/api/participants/', data=json.dumps(payload), content_type='application/json')
#     assert res.status_code == 201
#     data = res.get_json()
#     assert "participant_id" in data
#     assert isinstance(data["participant_id"], int)
#
# def test_register_participant_missing_fields(client):
#     # Fehlendes Alter
#     payload = {
#         "gender": "female",
#         "handedness": "left"
#     }
#     res = client.post('/api/participants/', data=json.dumps(payload), content_type='application/json')
#     assert res.status_code == 400
#     data = res.get_json()
#     assert "error" in data
#
# def test_submit_participant_success(client):
#     # Erst einen Teilnehmer registrieren
#     register_payload = {
#         "age": 30,
#         "gender": "diverse",
#         "handedness": "ambi"
#     }
#     reg_res = client.post('/api/participants/', json=register_payload)
#     participant_id = reg_res.get_json()["participant_id"]
#
#     submit_payload = {
#         "experiment_id": 1,
#         "slot": 1,
#         "participant_id": participant_id
#     }
#     res = client.post('/api/participants/submit', json=submit_payload)
#     assert res.status_code == 200
#     assert res.get_json()["status"] == "ok"
#
# def test_submit_participant_missing_data(client):
#     # Fehlende slot-Info
#     payload = {
#         "experiment_id": 1,
#         "participant_id": 123
#     }
#     res = client.post('/api/participants/submit', json=payload)
#     assert res.status_code == 400
#     assert "error" in res.get_json()
#
# def test_get_status_initial_false(client):
#     res = client.get('/api/participants/status/99?experiment_id=999')
#     assert res.status_code == 200
#     data = res.get_json()
#     assert data["submitted"] is False
#     assert data["participant_id"] is None
#
# def test_get_status_after_submit(client):
#     # Teilnehmer registrieren
#     reg_payload = {
#         "age": 35,
#         "gender": "female",
#         "handedness": "right"
#     }
#     reg_res = client.post('/api/participants/', json=reg_payload)
#     participant_id = reg_res.get_json()["participant_id"]
#
#     # Eintragen als "submitted"
#     submit_payload = {
#         "experiment_id": 123,
#         "slot": 5,
#         "participant_id": participant_id
#     }
#     client.post('/api/participants/submit', json=submit_payload)
#
#     # Status abrufen
#     res = client.get('/api/participants/status/5?experiment_id=123')
#     data = res.get_json()
#     assert res.status_code == 200
#     assert data["submitted"] is True
#     assert data["participant_id"] == participant_id
