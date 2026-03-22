from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, Any


# ─── Inferentielle Analyse ───────────────────────────────────────────────

class NormalityResult(BaseModel):
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    is_normal: Optional[bool] = None


class PostHocPair(BaseModel):
    condition_a: str
    condition_b: str
    p_corrected: Optional[float] = None
    effect_size_d: Optional[float] = None
    effect_size_cliffs_delta: Optional[float] = None
    significant: Optional[bool] = None


class MainEffect(BaseModel):
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None       # η²p oder Kendall's W
    effect_size_type: Optional[str] = None    # "eta2p", "kendalls_w"
    significant: Optional[bool] = None
    effect_size_d: Optional[float] = None
    effect_size_cliffs_delta: Optional[float] = None


class InferentialResult(BaseModel):
    test_used: str
    n_conditions: int
    normality: Optional[dict[str, NormalityResult]] = None
    sphericity_p: Optional[float] = None
    sphericity_correction: Optional[str] = None
    main_effect: Optional[MainEffect] = None
    posthoc: Optional[list[PostHocPair]] = None


# ─── Performance-Analyse ─────────────────────────────────────────────────

class PhaseStats(BaseModel):
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    n: Optional[int] = None


class ConditionPerformance(BaseModel):
    phase1: Optional[PhaseStats] = None
    phase2: Optional[PhaseStats] = None
    phase3: Optional[PhaseStats] = None
    total: Optional[PhaseStats] = None


class PerformanceAnalysisResponse(BaseModel):
    study_id: int
    performance: Optional[dict[str, Any]] = None  # by_condition + inferential


# ─── Korrelation ─────────────────────────────────────────────────────────

class CorrelationPair(BaseModel):
    var_a: str
    var_b: str
    r: Optional[float] = None
    p_uncorrected: Optional[float] = None
    p_corrected: Optional[float] = None
    significant: Optional[bool] = None
    method: Optional[str] = None
    interpretation: Optional[str] = None
    n: Optional[int] = None


class CorrelationMatrixResponse(BaseModel):
    pairs: list[CorrelationPair]
    n_pairs: int
    alpha_corrected: float


# ─── Cross-Study ─────────────────────────────────────────────────────────

class ConditionSummary(BaseModel):
    mean: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    n: Optional[int] = None
    std: Optional[float] = None


class CrossStudyResponse(BaseModel):
    metric: str
    is_descriptive_only: bool
    warning: str
    conditions: dict[str, ConditionSummary]
    baseline_ms: Optional[float] = None


# ─── Explorative Analyse ─────────────────────────────────────────────────

class PCAResponse(BaseModel):
    explained_variance_ratio: list[float]
    cumulative_variance: list[float]
    n_components: int
    n_observations: int
    variable_names: list[str]
    components: list[dict[str, float]]
    loadings: dict[str, dict[str, float]]


class ClusteringResponse(BaseModel):
    labels: list[int]
    n_clusters: int
    n_observations: int
    cluster_sizes: dict[int, int]
    linkage_method: str
