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


def test_get_study_response_structure(client, study_id):
    """GET /studies/{id} must return config, stimuli and questionnaires – no 500 recursion."""
    resp = client.get(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "config" in data
    assert "stimuli" in data
    assert "questionnaires" in data
    assert isinstance(data["stimuli"], list)
    assert isinstance(data["questionnaires"], list)


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


def test_get_experiments_by_study_includes_trials_field(client, study_id, experiment_id):
    """Each experiment in GET /studies/{id}/experiments must have a trials key."""
    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    exp = next(e for e in data if e["experiment_id"] == experiment_id)
    assert "trials" in exp
    assert isinstance(exp["trials"], list)


def test_get_experiments_by_study_trials_with_slots(client, study_id, experiment_id):
    """Saved trials must appear with slot data in GET /studies/{id}/experiments."""
    trial_payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": 1, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)

    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    exp = next(e for e in data if e["experiment_id"] == experiment_id)
    assert len(exp["trials"]) == 1, f"Expected 1 trial in experiment, found {len(exp['trials'])}"
    trial = exp["trials"][0]
    assert "slots" in trial
    assert isinstance(trial["slots"], list)


def test_close_study(client, study_id):
    resp = client.post(f"/studies/{study_id}/close")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["ended_at"] is not None


def test_get_experiments_by_study_not_found(client):
    """GET /studies/9999/experiments → 404 for unknown study."""
    resp = client.get("/studies/9999/experiments")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_participants_by_study_not_found(client):
    """GET /studies/9999/participants → 404 for unknown study."""
    resp = client.get("/studies/9999/participants")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

# ---------------------------------------------------------------------------
# study_service direct tests — stimuli and questionnaire paths
# ---------------------------------------------------------------------------

def test_create_study_with_stimuli(db_session):
    """create_study stores stimuli links when stimuli list is provided."""
    from Backend.models.stimulus import StimulusType
    from Backend.models.study.study_stimuli import StudyStimuli
    from Backend.db_session import SessionLocal
    from Backend.services.study_service import create_study

    st = StimulusType(type_name="test_condition")
    db_session.add(st)
    db_session.commit()

    data = {"status": "Aktiv", "stimuli": [{"stimuli_type_id": st.stimulus_type_id}]}
    session = SessionLocal()
    study = create_study(session, data)
    session.commit()
    study_id = study.study_id
    stimuli_rows = session.query(StudyStimuli).filter_by(study_id=study_id).all()
    session.close()

    assert len(stimuli_rows) == 1, f"Expected 1 row, found {len(stimuli_rows)}"
    assert stimuli_rows[0].stimuli_type_id == st.stimulus_type_id


def test_create_study_with_questionnaires(db_session):
    """create_study stores questionnaire links when questionnaires list is provided."""
    from Backend.models.questionnaire import Questionnaire
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.db_session import SessionLocal
    from Backend.services.study_service import create_study

    q = Questionnaire(name="Test-Q-Create")
    db_session.add(q)
    db_session.commit()

    data = {"status": "Aktiv", "questionnaires": [{"questionnaire_id": q.questionnaire_id}]}
    session = SessionLocal()
    study = create_study(session, data)
    session.commit()
    study_id = study.study_id
    sq_rows = session.query(StudyQuestionnaire).filter_by(study_id=study_id).all()
    session.close()

    assert len(sq_rows) == 1, f"Expected 1 row, found {len(sq_rows)}"
    assert sq_rows[0].questionnaire_id == q.questionnaire_id


def test_update_study_questionnaires_replace(db_session, study_id):
    """update_study deletes old questionnaire links and creates new ones."""
    from Backend.models.questionnaire import Questionnaire
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.db_session import SessionLocal
    from Backend.services.study_service import update_study

    q1 = Questionnaire(name="Q-Old")
    q2 = Questionnaire(name="Q-New")
    db_session.add_all([q1, q2])
    db_session.commit()

    # Initial: link q1
    session = SessionLocal()
    update_study(session, study_id, {"questionnaires": [{"questionnaire_id": q1.questionnaire_id}]})
    session.commit()
    session.close()

    # Replace: link q2
    session = SessionLocal()
    update_study(session, study_id, {"questionnaires": [{"questionnaire_id": q2.questionnaire_id}]})
    session.commit()
    sq_rows = session.query(StudyQuestionnaire).filter_by(study_id=study_id).all()
    session.close()

    assert len(sq_rows) == 1, f"Expected 1 row after replace, found {len(sq_rows)}"
    assert sq_rows[0].questionnaire_id == q2.questionnaire_id


def test_update_study_stimuli_replace(db_session, study_id):
    """update_study deletes old stimuli links and creates new ones."""
    from Backend.models.stimulus import StimulusType
    from Backend.models.study.study_stimuli import StudyStimuli
    from Backend.db_session import SessionLocal
    from Backend.services.study_service import update_study

    st1 = StimulusType(type_name="cond_old")
    st2 = StimulusType(type_name="cond_new")
    db_session.add_all([st1, st2])
    db_session.commit()

    # Initial
    session = SessionLocal()
    update_study(session, study_id, {"stimuli": [{"stimuli_type_id": st1.stimulus_type_id}]})
    session.commit()
    session.close()

    # Replace
    session = SessionLocal()
    update_study(session, study_id, {"stimuli": [{"stimuli_type_id": st2.stimulus_type_id}]})
    session.commit()
    stim_rows = session.query(StudyStimuli).filter_by(study_id=study_id).all()
    session.close()

    assert len(stim_rows) == 1, f"Expected 1 row after replace, found {len(stim_rows)}"
    assert stim_rows[0].stimuli_type_id == st2.stimulus_type_id
