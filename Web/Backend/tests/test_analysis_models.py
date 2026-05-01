from Backend.models.analysis import (
    InferentialResult, PerformanceAnalysisResponse,
    CorrelationMatrixResponse, CrossStudyResponse,
    PCAResponse, ClusteringResponse, CorrelationPair, ConditionSummary
)


def test_inferential_result_model():
    result = InferentialResult(test_used="rm_anova", n_conditions=3)
    assert result.test_used == "rm_anova"
    assert result.posthoc is None


def test_correlation_matrix_response():
    pair = CorrelationPair(var_a="a", var_b="b", r=0.8, significant=True, n=10)
    response = CorrelationMatrixResponse(pairs=[pair], n_pairs=1, alpha_corrected=0.05)
    assert len(response.pairs) == 1
    assert response.pairs[0].r == 0.8


def test_cross_study_response():
    cond = ConditionSummary(mean=310.5, ci_lower=290.0, ci_upper=330.0, n=20)
    response = CrossStudyResponse(
        metric="transfer_duration_ms",
        is_descriptive_only=True,
        warning="Cross-Study ist deskriptiv",
        conditions={"HS1_visual": cond},
        baseline_ms=300.0,
    )
    assert response.baseline_ms == 300.0
    assert response.is_descriptive_only is True


def test_pca_response():
    response = PCAResponse(
        explained_variance_ratio=[0.6, 0.25],
        cumulative_variance=[0.6, 0.85],
        n_components=2,
        n_observations=10,
        variable_names=["a", "b"],
        components=[{"PC1": 0.5, "PC2": -0.3}] * 10,
        loadings={"a": {"PC1": 0.7, "PC2": 0.2}, "b": {"PC1": -0.4, "PC2": 0.8}},
    )
    assert response.n_components == 2
