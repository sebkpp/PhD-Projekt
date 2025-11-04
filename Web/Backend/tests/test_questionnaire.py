# import pytest
# from Backend.db_session import SessionLocal
# from Backend.services.questionnaire_service import create_questionnaire_with_items
# from Backend.services.questionnaire_response_service import save_questionnaire_responses
# from Backend.models.participant import Participant
# from Backend.models.trial.trial import Trial
# from Backend.models.experiment import Experiment
# @pytest.fixture(scope="function")
# def setup_questionnaire():
#     session = SessionLocal()
#     questionnaire = create_questionnaire_with_items(session, "test_questionnaire", ["item1", "item2"])
#     session.commit()
#     session.close()
#     return questionnaire
#
# @pytest.fixture
# def setup_participant_and_trial():
#     session = SessionLocal()
#
#     # Erstelle ein Experiment
#     experiment = Experiment(
#         name="Testexperiment",
#         description="Experiment für Tests",
#         researcher="Testforscher"
#     )
#     session.add(experiment)
#     session.commit()
#
#     # Erstelle einen Trial, der zu diesem Experiment gehört
#     trial = Trial(
#         experiment_id=experiment.experiment_id,
#         trial_number=1
#     )
#     session.add(trial)
#     session.commit()
#
#     # Erstelle einen Participant
#     participant = Participant(
#         gender="diverse",
#         age=30,
#         handedness="right"
#     )
#     session.add(participant)
#     session.commit()
#
#     # Hole die IDs für den Test zurück
#     yield {
#         "participant_id": participant.participant_id,
#         "trial_id": trial.trial_id
#     }
#
#     session.close()
#
# def test_submit_questionnaire_response(client, clean_db, setup_questionnaire, setup_participant_and_trial):
#     participant_id = setup_participant_and_trial["participant_id"]
#     trial_id = setup_participant_and_trial["trial_id"]
#
#     payload = {
#         "participant_id": participant_id,
#         "trial_id": trial_id,
#         "questionnaire_name": "test_questionnaire",
#         "responses": {
#             "item1": 42,
#             "item2": 17
#         }
#     }
#
#     res = client.post('/api/submit-questionnaire', json=payload)
#     print("RESPONSE DATA:", res.get_data(as_text=True))  # <== NEU
#
#     assert res.status_code == 200
#     json_data = res.get_json()
#     assert json_data["status"] == "ok"
#     assert "Antworten gespeichert" in json_data["message"]
#
# def test_submit_questionnaire_response_missing_fields(client):
#     res = client.post('/api/submit-questionnaire', json={})
#     assert res.status_code == 400
#     assert "error" in res.get_json()
#
# def test_get_questionnaire_responses(client, clean_db, setup_questionnaire, setup_participant_and_trial):
#     participant_id = setup_participant_and_trial["participant_id"]
#     trial_id = setup_participant_and_trial["trial_id"]
#
#     session = SessionLocal()
#     save_questionnaire_responses(session, participant_id, trial_id, "test_questionnaire", {"item1": 10, "item2": 20})
#     session.close()
#
#     res = client.get('/api/questionnaire-responses', query_string={
#         "participant_id": participant_id,
#         "trial_id": trial_id,
#         "questionnaire_name": "test_questionnaire"
#     })
#
#     assert res.status_code == 200
#     data = res.get_json()
#     assert data["status"] == "ok"
#     assert data["data"]["item1"] == 10
#     assert data["data"]["item2"] == 20
#
# def test_get_questionnaires(client, clean_db, setup_questionnaire):
#     res = client.get('/api/questionnaires')
#     assert res.status_code == 200
#     data = res.get_json()
#     assert data["status"] == "ok"
#     assert any(q["name"] == "test_questionnaire" for q in data["data"])
#
# def test_create_questionnaire(client, clean_db):
#     payload = {
#         "name": "new_questionnaire",
#         "items": ["a", "b", "c"]
#     }
#
#     res = client.post('/api/questionnaire', json=payload)
#     assert res.status_code == 200 or res.status_code == 201
#     data = res.get_json()
#     assert data["status"] == "ok"
#     assert data["name"] == "new_questionnaire"
#     assert set(data["items"]) == set(["a", "b", "c"])
