from starlette import status


def _create_questionnaire(client, name: str = "TestQ", items=None):
    if items is None:
        items = ["Frage 1", "Frage 2"]
    resp = client.post("/questionnaires/", json={"name": name, "items": items})
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()


def test_create_questionnaire(client):
    resp = client.post("/questionnaires/", json={
        "name": "NASA-TLX",
        "items": ["Mental Demand", "Physical Demand", "Temporal Demand"]
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["status"] == "ok"
    assert "questionnaire_id" in data
    assert "items" in data
    assert len(data["items"]) == 3
    # Neue Felder prüfen
    assert "scale_type" in data
    assert "scale_min" in data
    assert "scale_max" in data


def test_create_questionnaire_with_metadata(client):
    resp = client.post("/questionnaires/", json={
        "name": "SUS",
        "scale_type": "likert",
        "scale_min": 1,
        "scale_max": 5,
        "items": [
            {
                "item_name": "q1",
                "item_label": "Ich finde das System einfach zu bedienen.",
                "min_label": "Stimme nicht zu",
                "max_label": "Stimme zu",
                "order_index": 0
            }
        ]
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["scale_type"] == "likert"
    assert data["scale_min"] == 1
    assert data["scale_max"] == 5
    assert len(data["items"]) == 1
    assert data["items"][0]["item_label"] == "Ich finde das System einfach zu bedienen."


def test_list_questionnaires(client):
    _create_questionnaire(client)
    resp = client.get("/questionnaires/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def _create_trial_and_get_id(client, experiment_id: int, participant_id: int) -> int:
    payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": participant_id, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    client.post(f"/experiments/{experiment_id}/trials", json=payload)
    from Backend.db_session import SessionLocal
    from Backend.models.trial.trial import Trial
    session = SessionLocal()
    trial = session.query(Trial).first()
    session.close()
    assert trial is not None
    return trial.trial_id


def test_submit_questionnaire_responses(client, experiment_id, participant_id):
    # Create questionnaire first
    _create_questionnaire(client, "NASA-TLX", ["Mental Demand", "Physical Demand"])
    trial_id = _create_trial_and_get_id(client, experiment_id, participant_id)

    resp = client.post("/questionnaires/submit", json={
        "participant_id": participant_id,
        "trial_id": trial_id,
        "questionnaire_name": "NASA-TLX",
        "responses": {"Mental Demand": 5, "Physical Demand": 3}
    })
    assert resp.status_code == status.HTTP_200_OK


def test_get_questionnaire_responses(client, experiment_id, participant_id):
    _create_questionnaire(client, "NASA-TLX-Get", ["Mental Demand"])
    trial_id = _create_trial_and_get_id(client, experiment_id, participant_id)

    client.post("/questionnaires/submit", json={
        "participant_id": participant_id,
        "trial_id": trial_id,
        "questionnaire_name": "NASA-TLX-Get",
        "responses": {"Mental Demand": 5}
    })

    resp = client.get("/questionnaires/responses", params={
        "participant_id": participant_id,
        "trial_id": trial_id,
        "questionnaire_name": "NASA-TLX-Get"
    })
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


def test_questionnaire_done_experiment(client, experiment_id, participant_id):
    resp = client.get("/questionnaires/done", params={
        "participant": participant_id,
        "experiment": experiment_id
    })
    assert resp.status_code == status.HTTP_200_OK
    assert "allDone" in resp.json()


def test_questionnaire_trial_done(client, experiment_id, participant_id):
    trial_payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": participant_id, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)

    from Backend.db_session import SessionLocal
    from Backend.models.trial.trial import Trial
    session = SessionLocal()
    trial = session.query(Trial).first()
    session.close()

    resp = client.get("/questionnaires/trial_done", params={
        "participant": participant_id,
        "trial": trial.trial_id
    })
    assert resp.status_code == status.HTTP_200_OK
    assert "allDone" in resp.json()


def test_get_by_experiment_participant(client, experiment_id, participant_id):
    resp = client.get(
        f"/questionnaires/experiments/{experiment_id}/participants/{participant_id}/questionnaires"
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "questionnaires" in resp.json()


def test_get_responses_for_experiment(client, experiment_id):
    resp = client.get(f"/questionnaires/experiments/{experiment_id}/questionnaire-responses")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


def test_get_questionnaires_by_study(client, study_id):
    resp = client.get(f"/questionnaires/study/{study_id}")
    assert resp.status_code == status.HTTP_200_OK


def test_get_questionnaire_not_found(client):
    """GET /questionnaires/9999 → 404 für unbekannte questionnaire_id."""
    resp = client.get("/questionnaires/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

# ---------------------------------------------------------------------------
# Questionnaire response service — seeded data paths
# ---------------------------------------------------------------------------

def test_are_all_questionnaires_in_trial_done_true(db_session, study_id, experiment_id, participant_id):
    """Returns True when all questionnaire items for a trial have responses."""
    from Backend.models.trial.trial import Trial
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.db_session import SessionLocal
    from Backend.services.questionnaire_response_service import are_all_questionnaires_in_trial_done

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    q = Questionnaire(name="Q-Done-Test")
    db_session.add(q)
    db_session.flush()
    # Link questionnaire to study so get_by_trial_id can find it
    db_session.add(StudyQuestionnaire(study_id=study_id, questionnaire_id=q.questionnaire_id))
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="item1", order_index=0)
    db_session.add(item)
    db_session.flush()
    db_session.add(QuestionnaireResponse(
        trial_id=trial.trial_id,
        participant_id=participant_id,
        questionnaire_item_id=item.questionnaire_item_id,
        response_value=75.0,
    ))
    db_session.commit()

    session = SessionLocal()
    result = are_all_questionnaires_in_trial_done(session, participant_id, trial.trial_id)
    session.close()
    assert result is True


def test_are_all_questionnaires_done_true(db_session, study_id, experiment_id, participant_id):
    """Returns True when all trials in an experiment are fully answered."""
    from Backend.models.trial.trial import Trial
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.db_session import SessionLocal
    from Backend.services.questionnaire_response_service import are_all_questionnaires_done

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    q = Questionnaire(name="Q-AllDone")
    db_session.add(q)
    db_session.flush()
    # Link questionnaire to study so get_by_trial_id can find it
    db_session.add(StudyQuestionnaire(study_id=study_id, questionnaire_id=q.questionnaire_id))
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="item1", order_index=0)
    db_session.add(item)
    db_session.flush()
    db_session.add(QuestionnaireResponse(
        trial_id=trial.trial_id,
        participant_id=participant_id,
        questionnaire_item_id=item.questionnaire_item_id,
        response_value=60.0,
    ))
    db_session.commit()

    session = SessionLocal()
    result = are_all_questionnaires_done(session, participant_id, experiment_id)
    session.close()
    assert result is True


def test_get_questionnaire_responses_for_experiment_with_data(
    db_session, experiment_id, participant_id
):
    """get_questionnaire_responses_for_experiment returns participant data when responses exist."""
    from Backend.models.trial.trial import Trial
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.db_session import SessionLocal
    from Backend.services.questionnaire_response_service import get_questionnaire_responses_for_experiment

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    q = Questionnaire(name="Q-ForExp")
    db_session.add(q)
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="item1", order_index=0)
    db_session.add(item)
    db_session.flush()
    db_session.add(QuestionnaireResponse(
        trial_id=trial.trial_id,
        participant_id=participant_id,
        questionnaire_item_id=item.questionnaire_item_id,
        response_value=55.0,
    ))
    db_session.commit()

    session = SessionLocal()
    result = get_questionnaire_responses_for_experiment(session, experiment_id)
    session.close()
    assert "participants" in result
    assert len(result["participants"]) == 1


# ---------------------------------------------------------------------------
# GET /questionnaires/{id} — 200 path
# ---------------------------------------------------------------------------

def test_get_questionnaire_by_id_200(client):
    """GET /questionnaires/{id} returns 200 when questionnaire exists."""
    # Create via POST
    resp = client.post("/questionnaires/", json={
        "name": "Test-Q-ById",
        "scale_type": "slider",
        "scale_min": 0,
        "scale_max": 100,
        "items": ["item_one"]
    })
    assert resp.status_code == 201
    q_id = resp.json()["questionnaire_id"]

    # Fetch by ID
    resp2 = client.get(f"/questionnaires/{q_id}")
    assert resp2.status_code == 200
    assert resp2.json()["questionnaire_id"] == q_id
