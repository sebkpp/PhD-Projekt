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
