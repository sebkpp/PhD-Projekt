import pytest
from Backend.services.data_analysis.exploratory_service import run_pca, run_clustering


@pytest.fixture
def sample_data():
    """10 Beobachtungen, 4 Variablen."""
    return {
        "transfer_time": [300, 320, 280, 310, 295, 330, 270, 315, 305, 290],
        "nasa_tlx": [60, 65, 55, 62, 58, 67, 52, 64, 61, 57],
        "ppi": [25, 20, 30, 23, 28, 18, 33, 22, 26, 29],
        "saccade_rate": [3.2, 3.8, 2.9, 3.5, 3.1, 4.0, 2.7, 3.6, 3.3, 3.0],
    }


def test_run_pca_basic(sample_data):
    result = run_pca(sample_data, n_components=2)
    assert result is not None
    assert result["n_components"] == 2
    assert result["n_observations"] == 10
    assert len(result["explained_variance_ratio"]) == 2
    assert len(result["components"]) == 10
    assert "PC1" in result["components"][0]
    assert "PC2" in result["components"][0]
    assert sum(result["explained_variance_ratio"]) <= 1.01  # max 100%


def test_run_pca_loadings(sample_data):
    result = run_pca(sample_data, n_components=2)
    assert result is not None
    for var in sample_data.keys():
        assert var in result["loadings"]
        assert "PC1" in result["loadings"][var]


def test_run_pca_too_few_variables():
    result = run_pca({"only_one": [1, 2, 3]}, n_components=2)
    assert result is None


def test_run_pca_unequal_lengths():
    result = run_pca({"a": [1, 2, 3], "b": [1, 2]}, n_components=2)
    assert result is None


def test_run_clustering_basic(sample_data):
    result = run_clustering(sample_data, n_clusters=3)
    assert result is not None
    assert result["n_clusters"] == 3
    assert result["n_observations"] == 10
    assert len(result["labels"]) == 10
    assert sum(result["cluster_sizes"].values()) == 10


def test_run_clustering_too_few():
    data = {"a": [1, 2], "b": [3, 4]}
    result = run_clustering(data, n_clusters=5)  # mehr Cluster als Beobachtungen → capped
    assert result is not None
    assert result["n_clusters"] == 2  # min(5, n=2)


def test_run_clustering_single_variable():
    result = run_clustering({"only": [1, 2, 3]}, n_clusters=2)
    assert result is None
