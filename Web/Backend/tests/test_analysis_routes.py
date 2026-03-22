"""
Tests for the new analysis API endpoints added in Task 13.
These tests do NOT require a database connection — they exercise only the
computation endpoints (correlation, cross-study, PCA, clustering).
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from Backend.app import app

client = TestClient(app)


def test_correlation_endpoint_basic():
    payload = {
        "variables": {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 3.0, 5.0, 6.0],
        }
    }
    response = client.post("/analysis/correlation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "pairs" in data
    assert data["n_pairs"] == 1


def test_correlation_endpoint_too_few_variables():
    payload = {"variables": {"x": [1.0, 2.0, 3.0]}}
    response = client.post("/analysis/correlation", json=payload)
    assert response.status_code == 400


def test_cross_study_endpoint():
    payload = {
        "study_data": {
            "HS1": [300.0, 320.0, 310.0, 290.0, 305.0],
            "HS2": [280.0, 295.0, 288.0, 270.0, 285.0],
        },
        "metric": "transfer_duration_ms"
    }
    response = client.post("/analysis/cross-study", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_descriptive_only"] is True
    assert data["baseline_ms"] == 300.0


def test_pca_endpoint_basic():
    payload = {
        "data": {
            "var_a": [1.0, 2.0, 3.0, 4.0, 5.0],
            "var_b": [5.0, 4.0, 3.0, 2.0, 1.0],
        },
        "n_components": 2
    }
    response = client.post("/analysis/pca", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "explained_variance_ratio" in data
    assert data["n_observations"] == 5


def test_pca_endpoint_too_few_variables():
    payload = {"data": {"only": [1.0, 2.0, 3.0]}, "n_components": 2}
    response = client.post("/analysis/pca", json=payload)
    assert response.status_code == 400


def test_clustering_endpoint_basic():
    payload = {
        "data": {
            "var_a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "var_b": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
        },
        "n_clusters": 2
    }
    response = client.post("/analysis/clustering", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert data["n_clusters"] == 2
    assert data["n_observations"] == 6


def test_clustering_endpoint_too_few_variables():
    payload = {"data": {"only": [1.0, 2.0, 3.0]}, "n_clusters": 2}
    response = client.post("/analysis/clustering", json=payload)
    assert response.status_code == 400
