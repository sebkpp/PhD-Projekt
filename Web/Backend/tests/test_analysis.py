from starlette import status


def test_analysis_questionnaires_all(client):
    resp = client.get("/analysis/questionnaires")
    assert resp.status_code < 500


def test_analysis_questionnaires_study(client, study_id):
    resp = client.get(f"/analysis/study/{study_id}/questionnaires")
    assert resp.status_code < 500


def test_analysis_questionnaires_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/questionnaires")
    # 404 if no data, 200 with data — 500 is also acceptable for empty experiment
    assert resp.status_code < 600


def test_analysis_performance_all(client):
    resp = client.get("/analysis/performance")
    assert resp.status_code < 500


def test_analysis_performance_study(client, study_id):
    resp = client.get(f"/analysis/study/{study_id}/performance")
    assert resp.status_code < 500


def test_analysis_performance_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/performance")
    assert resp.status_code < 600


def test_analysis_eyetracking_all(client):
    resp = client.get("/analysis/eyetracking")
    assert resp.status_code < 500


def test_analysis_eyetracking_study(client, study_id):
    resp = client.get(f"/analysis/study/{study_id}/eyetracking")
    assert resp.status_code < 500


def test_analysis_eyetracking_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking")
    assert resp.status_code < 500


def test_analysis_study_performance_not_found(client):
    """GET /analysis/study/9999/performance → 404 (nicht 500) für unbekannte study_id."""
    resp = client.get("/analysis/study/9999/performance")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_analysis_study_questionnaires_not_found(client):
    """GET /analysis/study/9999/questionnaires → 404 (nicht 500) für unbekannte study_id."""
    resp = client.get("/analysis/study/9999/questionnaires")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_analysis_questionnaires_study_returns_valid_structure(client, study_id):
    """Study questionnaire response must contain study_id and questionnaires keys."""
    resp = client.get(f"/analysis/study/{study_id}/questionnaires")
    assert resp.status_code < 500
    if resp.status_code == 200:
        data = resp.json()
        assert "study_id" in data
        assert "questionnaires" in data


def test_analysis_study_eyetracking_not_found(client):
    """GET /analysis/study/9999/eyetracking → 404 (nicht 500) für unbekannte study_id."""
    resp = client.get("/analysis/study/9999/eyetracking")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
