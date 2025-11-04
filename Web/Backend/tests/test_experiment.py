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
# def test_create_experiment_success(client):
#     data = {
#         "name": "Test Experiment",
#         "description": "Testbeschreibung",
#         "researcher": "Tester"
#     }
#     response = client.post('/api/experiments', data=json.dumps(data), content_type='application/json')
#     assert response.status_code == 201
#     json_data = response.get_json()
#     assert "experiment_id" in json_data
#
# def test_create_experiment_missing_name(client):
#     data = {
#         "description": "Keine Name",
#         "researcher": "Tester"
#     }
#     response = client.post('/api/experiments', data=json.dumps(data), content_type='application/json')
#     assert response.status_code == 400
#     json_data = response.get_json()
#     assert "errors" in json_data
#     assert "name ist erforderlich." in json_data["errors"]
#
# def test_create_multiple_experiments(client):
#     names = ["Experiment A", "Experiment B"]
#     ids = []
#
#     for name in names:
#         res = client.post('/api/experiments', json={"name": name})
#         assert res.status_code == 201
#         ids.append(res.get_json()["experiment_id"])
#
#     assert len(ids) == 2
#     assert ids[0] != ids[1]
#
# def test_create_experiment_invalid_json(client):
#     response = client.post(
#         '/api/experiments',
#         data="nur text, kein json",
#         content_type='text/plain'
#     )
#     assert response.status_code in (400, 415)
#
# def test_cleanup(client):
#     # Experiment anlegen
#     client.post('/api/experiments', json={"name": "Temp Experiment"})
#
#     # Neue Session öffnen, um den DB-Status zu prüfen
#     from Backend.db_session import SessionLocal
#     from Backend.models.experiment import Experiment
#
#     session = SessionLocal()
#     experiments = session.query(Experiment).all()
#     session.close()
#
#     # Die Tabelle soll nicht leer sein, weil wir gerade einen Eintrag angelegt haben
#     assert len(experiments) == 1
#
#     # Jetzt Cleanup manuell durchführen (wenn nicht schon automatisch)
#     session = SessionLocal()
#     session.query(Experiment).delete()
#     session.commit()
#     session.close()
#
#     # Prüfen, ob nach Cleanup alles weg ist
#     session = SessionLocal()
#     experiments_after_cleanup = session.query(Experiment).all()
#     session.close()
#     assert len(experiments_after_cleanup) == 0
#
# def test_experiment_id_returned_and_unique(client):
#     response1 = client.post('/api/experiments', json={"name": "Test 1"})
#     response2 = client.post('/api/experiments', json={"name": "Test 2"})
#
#     assert response1.status_code == 201
#     assert response2.status_code == 201
#
#     data1 = response1.get_json()
#     data2 = response2.get_json()
#
#     assert "experiment_id" in data1
#     assert "experiment_id" in data2
#
#     id1 = data1["experiment_id"]
#     id2 = data2["experiment_id"]
#
#     assert id1 is not None
#     assert id2 is not None
#
#     # je nach Typ: z.B. beide unterschiedlich
#     assert id1 != id2