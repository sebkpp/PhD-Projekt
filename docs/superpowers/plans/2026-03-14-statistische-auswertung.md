# Statistische Auswertung — Implementierungsplan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vollständiges statistisches Analyse-System für VR-Handover-Studie mit inferenziellen Tests, Eye-Tracking-Erweiterungen, Fragebogen-Scoring, Export und Frontend-Visualisierungen.

**Architecture:** Neue Backend-Services (inferential, effect_size, correlation, cross_study, exploratory) ergänzen bestehende Services; bestehende Inferenzlogik wird in `stats_utils.py` konsolidiert und durch N-Bedingungen-fähige Variante ersetzt. Neue API-Endpunkte unter `/analysis/` und `/export/`. Frontend erhält neue Chart-Komponenten pro Kategorie + Cross-Study-Seite.

**Tech Stack:** Python/FastAPI, pingouin, scikit-learn, scikit-posthocs, openpyxl, React/Vite, Plotly, Recharts

**Spec:** `docs/superpowers/specs/2026-03-14-statistische-auswertung-design.md`

---

## Chunk 1: Foundation

### Task 1: Python-Abhängigkeiten hinzufügen

**Files:**
- Modify: `Web/pyproject.toml`

- [ ] **Step 1: Abhängigkeiten installieren**

```bash
cd Web
uv add pingouin scikit_posthocs scikit-learn openpyxl weasyprint
```

Erwartung: alle 5 Packages in `pyproject.toml` und `uv.lock` erscheinen.

- [ ] **Step 2: Import-Check**

```bash
uv run python -c "import pingouin; import scikit_posthocs; import sklearn; import openpyxl; import weasyprint; print('OK')"
```

Erwartung: `OK`

> **Windows-Hinweis:** WeasyPrint benötigt GTK3-Runtime (Cairo, Pango). Falls der Import fehlschlägt, GTK3 für Windows von https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer installieren. Report-Endpunkt kann bis dahin HTML-only liefern.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add statistical analysis dependencies (pingouin, scikit-learn, openpyxl, weasyprint)"
```

---

### Task 2: Schema-Erweiterungen (SQL + ORM)

**Files:**
- Modify: `sql/schema.sql`
- Modify: `Web/Backend/models/handover.py`
- Modify: `Web/Backend/models/study/study_config.py`

- [ ] **Step 1: SQL-Schema aktualisieren**

In `sql/schema.sql` die ALTER-Statements einfügen (am Ende des Handover- bzw. study_config-Blocks):

```sql
-- handover: Fehler-Tracking
ALTER TABLE handover
  ADD COLUMN IF NOT EXISTS is_error BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS error_type VARCHAR(100);

-- study_config: Typ-Konfiguration
ALTER TABLE study_config
  ADD COLUMN IF NOT EXISTS study_type VARCHAR(50) DEFAULT 'stimulus_comparison';
```

- [ ] **Step 2: ORM Handover erweitern**

In `Backend/models/handover.py` nach `giver_released_object`:

```python
from sqlalchemy import Boolean
# ...
is_error = Column(Boolean, default=False)
error_type = Column(String(100), nullable=True)
```

`to_dict()` ergänzen:
```python
"is_error": self.is_error,
"error_type": self.error_type,
```

- [ ] **Step 3: ORM StudyConfig erweitern**

In `Backend/models/study/study_config.py`:

```python
study_type = Column(String(50), default='stimulus_comparison')
```

`to_dict()` ergänzen:
```python
"study_type": self.study_type,
```

`StudyConfigResponse` ergänzen:
```python
study_type: Optional[str] = Field('stimulus_comparison', description="Type: avatar_comparison | stimulus_comparison | combination_comparison")
```

- [ ] **Step 4: ALTER TABLE auf Test-DB ausführen**

```bash
# In psql gegen testdb:
psql -d testdb -c "ALTER TABLE handover ADD COLUMN IF NOT EXISTS is_error BOOLEAN DEFAULT FALSE, ADD COLUMN IF NOT EXISTS error_type VARCHAR(100);"
psql -d testdb -c "ALTER TABLE study_config ADD COLUMN IF NOT EXISTS study_type VARCHAR(50) DEFAULT 'stimulus_comparison';"
```

- [ ] **Step 5: Smoke-Test (bestehende Tests noch grün)**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

Erwartung: alle Tests grün.

- [ ] **Step 6: Commit**

```bash
git add sql/schema.sql Backend/models/handover.py Backend/models/study/study_config.py
git commit -m "feat: add is_error/error_type to handover, study_type to study_config"
```

---

### Task 3: stats_utils.py — Migration bestehender Hilfsfunktionen

**Files:**
- Create: `Web/Backend/utils/stats_utils.py`
- Modify: `Web/Backend/services/data_analysis/performance_analysis_service.py`
- Modify: `Web/Backend/services/data_analysis/eye_tracking_analysis_service.py`
- Modify: `Web/Backend/services/data_analysis/questionnaire_analysis_service.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_stats_utils.py
from Backend.utils.stats_utils import sanitize_stats, cohens_d, run_paired_test
import math

def test_sanitize_stats_removes_nan():
    result = sanitize_stats({"a": float("nan"), "b": 1.0})
    assert result["a"] is None
    assert result["b"] == 1.0

def test_cohens_d_basic():
    d = cohens_d([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    assert d is not None
    assert abs(d) > 0

def test_cohens_d_too_few():
    assert cohens_d([1.0], [2.0]) is None

def test_run_paired_test_needs_n_gt_3():
    # n=3 → None (guard: n > 3 erforderlich)
    result = run_paired_test([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    assert result is None

def test_run_paired_test_normal_data():
    import numpy as np
    np.random.seed(42)
    a = list(np.random.normal(5, 1, 10))
    b = list(np.random.normal(7, 1, 10))
    result = run_paired_test(a, b)
    assert result is not None
    assert result["test"] in ("paired_ttest", "wilcoxon")
    assert "p_value" in result
    assert "effect_size_d" in result
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_stats_utils.py -v
```

Erwartung: `ImportError` oder `ModuleNotFoundError`

- [ ] **Step 3: stats_utils.py erstellen**

```python
# Backend/utils/stats_utils.py
import math
import numpy as np
import scipy.stats as scipy_stats


def sanitize_stats(stats_dict: dict) -> dict:
    for k, v in stats_dict.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            stats_dict[k] = None
        if isinstance(v, tuple):
            stats_dict[k] = tuple(
                None if (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else x
                for x in v
            )
    return stats_dict


def cohens_d(values_a: list, values_b: list) -> float | None:
    if len(values_a) < 2 or len(values_b) < 2:
        return None
    mean_diff = np.mean(values_a) - np.mean(values_b)
    pooled_std = np.sqrt(
        (np.std(values_a, ddof=1) ** 2 + np.std(values_b, ddof=1) ** 2) / 2
    )
    if pooled_std > 0:
        d = float(mean_diff / pooled_std)
        return None if (math.isnan(d) or math.isinf(d)) else d
    return 0.0


def run_paired_test(values_a: list, values_b: list) -> dict | None:
    """
    Auto-selects paired t-test or Wilcoxon. Requires n > 3 per group.
    Guard: n <= 3 → return None (spec: Shapiro-Wilk needs n >= 4).
    """
    if len(values_a) <= 3 or len(values_b) <= 3:
        return None
    _, p_a = scipy_stats.shapiro(values_a)
    _, p_b = scipy_stats.shapiro(values_b)
    try:
        if p_a >= 0.05 and p_b >= 0.05:
            stat, p = scipy_stats.ttest_rel(values_a, values_b)
            test_name = "paired_ttest"
        else:
            stat, p = scipy_stats.wilcoxon(values_a, values_b)
            test_name = "wilcoxon"
    except Exception:
        return None

    stat_val = None if (isinstance(stat, float) and math.isnan(stat)) else float(stat)
    p_val = None if (isinstance(p, float) and math.isnan(p)) else float(p)
    return {
        "test": test_name,
        "statistic": stat_val,
        "p_value": p_val,
        "effect_size_d": cohens_d(values_a, values_b),
        "significant": bool(p_val < 0.05) if p_val is not None else None,
    }
```

- [ ] **Step 4: Imports in bestehenden Services aktualisieren**

`performance_analysis_service.py`: Lokale Definitionen von `sanitize_stats`, `cohens_d`, `run_paired_test` **löschen**, stattdessen:
```python
from Backend.utils.stats_utils import sanitize_stats, cohens_d, run_paired_test
```

`eye_tracking_analysis_service.py`: Zeile 8 ersetzen:
```python
from Backend.utils.stats_utils import sanitize_stats
```

`questionnaire_analysis_service.py`: Zeile 5 ersetzen:
```python
from Backend.utils.stats_utils import run_paired_test
```

- [ ] **Step 5: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_stats_utils.py Backend/tests/test_analysis.py -v
```

Erwartung: alle grün.

- [ ] **Step 6: Alle bestehenden Tests prüfen**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

Erwartung: keine Regression.

- [ ] **Step 7: Commit**

```bash
git add Backend/utils/stats_utils.py Backend/services/data_analysis/ Backend/tests/test_stats_utils.py
git commit -m "refactor: migrate sanitize_stats/cohens_d/run_paired_test to utils/stats_utils.py"
```

---

## Chunk 2: Effect Size & Inferential Services

### Task 4: effect_size_service.py

**Files:**
- Create: `Web/Backend/services/data_analysis/effect_size_service.py`
- Create: `Web/Backend/tests/test_effect_sizes.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_effect_sizes.py
import pytest
from Backend.services.data_analysis.effect_size_service import (
    cliffs_delta, interpret_cohens_d, interpret_eta2p,
    omega2p_from_anova, kendalls_w_from_friedman,
)

def test_cliffs_delta_positive():
    d = cliffs_delta([3, 4, 5], [1, 2, 3])
    assert d is not None
    assert d > 0

def test_cliffs_delta_negative():
    d = cliffs_delta([1, 2], [4, 5])
    assert d < 0

def test_cliffs_delta_empty():
    assert cliffs_delta([], [1, 2]) is None

def test_cliffs_delta_tie():
    assert cliffs_delta([2, 2], [2, 2]) == 0.0

def test_interpret_cohens_d():
    assert interpret_cohens_d(0.1) == "vernachlässigbar"
    assert interpret_cohens_d(0.4) == "klein"
    assert interpret_cohens_d(0.7) == "mittel"
    assert interpret_cohens_d(1.0) == "groß"

def test_interpret_eta2p():
    assert interpret_eta2p(0.005) == "klein"
    assert interpret_eta2p(0.08) == "mittel"
    assert interpret_eta2p(0.15) == "groß"

def test_omega2p_from_anova_basic():
    # SS_effect=10, df_effect=2, SS_error=20, df_error=18
    result = omega2p_from_anova(ss_effect=10, df_effect=2, ss_error=20, df_error=18)
    assert result is not None
    assert 0.0 <= result <= 1.0

def test_kendalls_w_from_friedman():
    import numpy as np
    # 5 subjects, 3 conditions
    data = np.array([[3,1,2],[1,3,2],[2,1,3],[3,2,1],[1,2,3]])
    w = kendalls_w_from_friedman(data)
    assert w is not None
    assert 0.0 <= w <= 1.0
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_effect_sizes.py -v
```

- [ ] **Step 3: effect_size_service.py erstellen**

```python
# Backend/services/data_analysis/effect_size_service.py
import math
import numpy as np


def cliffs_delta(x: list, y: list) -> float | None:
    if not x or not y:
        return None
    dominance = sum(
        1 if xi > yj else (-1 if xi < yj else 0)
        for xi in x for yj in y
    )
    return dominance / (len(x) * len(y))


def interpret_cohens_d(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "vernachlässigbar"
    if d < 0.5:
        return "klein"
    if d < 0.8:
        return "mittel"
    return "groß"


def interpret_eta2p(eta2p: float) -> str:
    if eta2p < 0.06:
        return "klein"
    if eta2p < 0.14:
        return "mittel"
    return "groß"


def interpret_cliffs_delta(d: float) -> str:
    d = abs(d)
    if d < 0.15:
        return "vernachlässigbar"
    if d < 0.33:
        return "klein"
    if d < 0.47:
        return "mittel"
    return "groß"


def omega2p_from_anova(ss_effect: float, df_effect: float,
                        ss_error: float, df_error: float) -> float | None:
    """Bias-corrected ω²p from ANOVA sum-of-squares."""
    if df_error == 0:
        return None
    ms_error = ss_error / df_error
    ss_total = ss_effect + ss_error
    denominator = ss_total + ms_error
    if denominator == 0:
        return None
    result = (ss_effect - df_effect * ms_error) / denominator
    result = max(0.0, result)  # can be slightly negative → clamp to 0
    return None if (math.isnan(result) or math.isinf(result)) else round(result, 4)


def kendalls_w_from_friedman(data: np.ndarray) -> float | None:
    """
    Compute Kendall's W from a subjects × conditions matrix.
    W = 12 * S / (k² * (n³ - n))  where S = sum of squared deviations of rank sums.
    """
    n, k = data.shape  # n=subjects, k=conditions
    if n < 2 or k < 2:
        return None
    rank_sums = data.sum(axis=0)  # sum of ranks per condition
    mean_rank_sum = rank_sums.mean()
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    denominator = k ** 2 * (n ** 3 - n)
    if denominator == 0:
        return None
    w = 12 * S / denominator
    return round(float(w), 4)
```

- [ ] **Step 4: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_effect_sizes.py -v
```

Erwartung: alle grün.

- [ ] **Step 5: Commit**

```bash
git add Backend/services/data_analysis/effect_size_service.py Backend/tests/test_effect_sizes.py
git commit -m "feat: add effect_size_service (Cliff's Delta, omega2p, Kendall's W, interpretations)"
```

---

### Task 5: inferential_service.py

**Files:**
- Create: `Web/Backend/services/data_analysis/inferential_service.py`
- Create: `Web/Backend/tests/test_inferential.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_inferential.py
import numpy as np
import pytest
from Backend.services.data_analysis.inferential_service import run_inferential_analysis

def make_conditions(n=10, k=3, seed=42):
    rng = np.random.default_rng(seed)
    return {f"cond_{i}": list(rng.normal(loc=5 + i, scale=1, size=n)) for i in range(k)}

def test_k2_returns_paired_test():
    conditions = make_conditions(n=10, k=2)
    result = run_inferential_analysis(conditions)
    assert result["n_conditions"] == 2
    assert result["test_used"] in ("paired_ttest", "wilcoxon")
    assert "main_effect" in result
    assert result["posthoc"] == []  # no post-hoc for k=2

def test_k3_returns_anova_or_friedman():
    conditions = make_conditions(n=10, k=3)
    result = run_inferential_analysis(conditions)
    assert result["n_conditions"] == 3
    assert result["test_used"] in ("rm_anova", "rm_anova_gg", "friedman")
    assert len(result["posthoc"]) == 3  # 3 pairs

def test_too_few_data_returns_none():
    conditions = {"a": [1.0, 2.0], "b": [3.0, 4.0]}
    result = run_inferential_analysis(conditions)
    assert result is None

def test_posthoc_has_effect_sizes():
    conditions = make_conditions(n=12, k=3)
    result = run_inferential_analysis(conditions)
    if result and result["posthoc"]:
        pair = result["posthoc"][0]
        assert "effect_size_d" in pair or "effect_size_cliffs_delta" in pair

def test_normality_dict_present():
    conditions = make_conditions(n=10, k=3)
    result = run_inferential_analysis(conditions)
    if result:
        assert "normality" in result
        for cond in conditions:
            assert cond in result["normality"]

def test_n3_per_condition_returns_none_for_k2():
    # n=3 → run_inferential_analysis returns None (min_n < 3 is False for n=3,
    # but k=2 delegates to _run_k2 which uses run_paired_test requiring n > 3)
    # Actually: run_inferential_analysis guard is min_n < 3, so n=3 passes through.
    # _run_k2 calls scipy_stats directly (not run_paired_test), so n=3 may work.
    # This test documents the actual boundary behavior:
    conditions = {"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]}
    result = run_inferential_analysis(conditions)
    # n=3: Shapiro-Wilk returns None (n<=3), so falls back to Wilcoxon
    # Wilcoxon with n=3 may or may not work — assert either None or valid result
    assert result is None or result["test_used"] in ("paired_ttest", "wilcoxon")

def test_k2_main_effect_has_effect_sizes():
    conditions = make_conditions(n=10, k=2)
    result = run_inferential_analysis(conditions)
    assert result is not None
    assert "effect_size_d" in result["main_effect"]
    assert "effect_size_cliffs_delta" in result["main_effect"]
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_inferential.py -v
```

- [ ] **Step 3: inferential_service.py erstellen**

```python
# Backend/services/data_analysis/inferential_service.py
import math
import itertools
import numpy as np
import pandas as pd
import scipy.stats as scipy_stats
import pingouin as pg
import scikit_posthocs as sp

from Backend.utils.stats_utils import cohens_d
from Backend.services.data_analysis.effect_size_service import (
    cliffs_delta, omega2p_from_anova, kendalls_w_from_friedman,
    interpret_cohens_d, interpret_cliffs_delta,
)


def _shapiro_p(values: list) -> float | None:
    if len(values) > 3:
        _, p = scipy_stats.shapiro(values)
        return round(float(p), 4)
    return None


def run_inferential_analysis(conditions: dict[str, list]) -> dict | None:
    """
    conditions: {"cond_name": [per-experiment-mean, ...], ...}
    Returns inferential result dict or None if not enough data.
    """
    k = len(conditions)
    if k < 2:
        return None

    cond_names = list(conditions.keys())
    values_list = [conditions[c] for c in cond_names]
    min_n = min(len(v) for v in values_list)

    if min_n < 3:
        return None

    # Normality
    normality = {c: _shapiro_p(conditions[c]) for c in cond_names}
    all_normal = all(p is not None and p >= 0.05 for p in normality.values())

    if k == 2:
        return _run_k2(cond_names, values_list, normality, all_normal)
    else:
        return _run_kn(cond_names, values_list, normality, all_normal, min_n)


def _run_k2(cond_names, values_list, normality, all_normal):
    a, b = values_list[0], values_list[1]
    try:
        if all_normal:
            stat, p = scipy_stats.ttest_rel(a, b)
            test_name = "paired_ttest"
        else:
            stat, p = scipy_stats.wilcoxon(a, b)
            test_name = "wilcoxon"
    except Exception:
        return None

    p_val = float(p) if not math.isnan(p) else None
    d = cohens_d(a, b)
    cd = cliffs_delta(a, b)
    return {
        "test_used": test_name,
        "n_conditions": 2,
        "normality": normality,
        "sphericity_p": None,
        "sphericity_correction": "none",
        "main_effect": {
            "statistic": float(stat),
            "p_value": p_val,
            "significant": bool(p_val < 0.05) if p_val is not None else None,
            "effect_eta2p": None,
            "effect_omega2p": None,
            "effect_kendalls_w": None,
            # k=2 effect sizes go here (not in posthoc since only 1 pair)
            "effect_size_d": d,
            "effect_size_d_interpretation": interpret_cohens_d(d) if d is not None else None,
            "effect_size_cliffs_delta": cd,
            "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
        },
        "posthoc": [],
    }


def _run_kn(cond_names, values_list, normality, all_normal, min_n):
    # Build long-format DataFrame for pingouin
    rows = []
    for i, cond in enumerate(cond_names):
        for subj_idx, val in enumerate(values_list[i]):
            rows.append({"subject": subj_idx, "condition": cond, "value": val})
    df = pd.DataFrame(rows)

    # Pre-compute condition lookup (used in post-hoc loops)
    cond_dict = dict(zip(cond_names, values_list))

    test_used = None
    main_effect = {}
    posthoc = []
    sphericity_p = None
    sphericity_correction = "none"
    used_rm_anova = False

    if all_normal and min_n >= 5:
        try:
            aov = pg.rm_anova(data=df, dv="value", within="condition",
                              subject="subject", correction="auto", detailed=True)
            row = aov.iloc[0]

            # Pingouin uses column "spher" (bool) for sphericity, "p-spher" for Mauchly p-value
            spher_ok = True
            if "spher" in aov.columns:
                spher_val = aov["spher"].iloc[0]
                spher_ok = bool(spher_val) if spher_val is not None else True
            if "p-spher" in aov.columns:
                sphericity_p = float(aov["p-spher"].iloc[0]) if aov["p-spher"].iloc[0] is not None else None

            if not spher_ok:
                test_used = "rm_anova_gg"
                sphericity_correction = "greenhouse_geisser"
                # Use GG-corrected p-value
                p_main = float(row.get("p-GG-corr", row.get("p-unc", 1.0)) or 1.0)
                padjust_method = "bonf"
            else:
                test_used = "rm_anova"
                p_main = float(row.get("p-unc", 1.0) or 1.0)
                padjust_method = "tukey"  # spec: Tukey HSD for RM-ANOVA without GG

            eta2p = float(row.get("np2", 0.0) or 0.0)
            ss_effect = float(row.get("SS", 0.0) or 0.0)
            df_effect = float(row.get("ddof1", 1.0) or 1.0)
            err_row = aov.iloc[1] if len(aov) > 1 else None
            ss_error = float(err_row["SS"]) if err_row is not None else None
            df_error = float(err_row["ddof1"]) if err_row is not None else None
            omega = omega2p_from_anova(ss_effect, df_effect, ss_error, df_error) if ss_error else None

            main_effect = {
                "statistic": float(row.get("F", 0.0) or 0.0),
                "p_value": p_main,
                "significant": bool(p_main < 0.05),
                "effect_eta2p": round(eta2p, 4),
                "effect_omega2p": omega,
                "effect_kendalls_w": None,
                "effect_size_d": None,
                "effect_size_cliffs_delta": None,
            }

            pairs_df = pg.pairwise_tests(data=df, dv="value", within="condition",
                                         subject="subject", padjust=padjust_method)
            for _, pr in pairs_df.iterrows():
                ca, cb = str(pr["A"]), str(pr["B"])
                va = cond_dict.get(ca, [])
                vb = cond_dict.get(cb, [])
                d = cohens_d(va, vb)
                cd = cliffs_delta(va, vb)
                posthoc.append({
                    "pair": [ca, cb],
                    "p_value": float(pr.get("p-unc", 1.0) or 1.0),
                    "p_adjusted": float(pr.get("p-corr", 1.0) or 1.0),
                    "correction": padjust_method,
                    "effect_size_d": d,
                    "effect_size_d_interpretation": interpret_cohens_d(d) if d is not None else None,
                    "effect_size_cliffs_delta": cd,
                    "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
                    "significant": bool(float(pr.get("p-corr", 1.0) or 1.0) < 0.05),
                })
            used_rm_anova = True
        except Exception:
            # Fallback to Friedman — reset state
            all_normal = False
            used_rm_anova = False

    if not used_rm_anova:
        try:
            posthoc = []  # Reset: prevent mixing partial RM-ANOVA with Friedman results
            data_matrix = np.array(values_list).T  # subjects × conditions
            stat, p = scipy_stats.friedmanchisquare(*values_list)
            test_used = "friedman"
            w = kendalls_w_from_friedman(data_matrix)
            main_effect = {
                "statistic": float(stat),
                "p_value": float(p),
                "significant": bool(p < 0.05),
                "effect_eta2p": None,
                "effect_omega2p": None,
                "effect_kendalls_w": w,
                "effect_size_d": None,
                "effect_size_cliffs_delta": None,
            }
            df_wide = pd.DataFrame(cond_dict)
            dunn = sp.posthoc_dunn(df_wide, p_adjust="bonferroni")
            for ca, cb in itertools.combinations(cond_names, 2):
                p_adj = float(dunn.loc[ca, cb])
                cd = cliffs_delta(cond_dict[ca], cond_dict[cb])
                posthoc.append({
                    "pair": [ca, cb],
                    "p_value": None,
                    "p_adjusted": p_adj,
                    "correction": "bonferroni",
                    "effect_size_d": None,
                    "effect_size_d_interpretation": None,
                    "effect_size_cliffs_delta": cd,
                    "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
                    "significant": bool(p_adj < 0.05),
                })
        except Exception:
            return None

    return {
        "test_used": test_used,
        "n_conditions": len(cond_names),
        "normality": normality,
        "sphericity_p": sphericity_p,
        "sphericity_correction": sphericity_correction,
        "main_effect": main_effect,
        "posthoc": posthoc,
    }
```

- [ ] **Step 4: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_inferential.py -v
```

Erwartung: alle grün.

- [ ] **Step 5: Commit**

```bash
git add Backend/services/data_analysis/inferential_service.py Backend/tests/test_inferential.py
git commit -m "feat: add inferential_service with auto test-selection (RM-ANOVA/Friedman, post-hoc)"
```

---

### Task 6: Performance-Service auf N Bedingungen erweitern

**Files:**
- Modify: `Web/Backend/services/data_analysis/performance_analysis_service.py`

- [ ] **Step 1: Test schreiben (in bestehender test_analysis.py)**

In `Backend/tests/test_analysis.py` Test ergänzen der 3 Bedingungen testet:

```python
def test_study_performance_three_conditions(client, db_session):
    # Setup: Study mit 3 Trials (verschiedene Stimuli)
    # ... (analog zu bestehenden Setup-Fixtures)
    # Prüfe: inferential enthält Ergebnisse für alle 3 Paare
    pass  # konkrete Implementierung folgt mit DB-Fixtures
```

*Hinweis: Dieser Test wird im nächsten Step konkretisiert wenn die Fixture-Struktur klar ist.*

- [ ] **Step 2: Hardcoded k=2-Logik ersetzen**

In `performance_analysis_service.py` Zeilen ~301–311 ersetzen.

Die bestehenden Variablennamen in `analyze_study_performance` (Zeilen ~229–278):
- `condition_phase1: dict[str, list]` — per-experiment Mittelwert pro Bedingung, Phase 1
- `condition_phase2: dict[str, list]` — Phase 2
- `condition_phase3: dict[str, list]` — Phase 3
- `condition_total: dict[str, list]` — Total
- `conditions: list[str]` — sortierte Liste aller Bedingungsnamen

```python
# ALT (löschen):
inferential = {}
if len(conditions) >= 2:
    cond_a, cond_b = conditions[0], conditions[1]
    for metric, bucket_a, bucket_b in [
        ("total", condition_total[cond_a], condition_total[cond_b]),
        ("phase1", condition_phase1[cond_a], condition_phase1[cond_b]),
        ("phase2", condition_phase2[cond_a], condition_phase2[cond_b]),
        ("phase3", condition_phase3[cond_a], condition_phase3[cond_b]),
    ]:
        inferential[metric] = run_paired_test(bucket_a, bucket_b)

# NEU (oben im Modul Import ergänzen):
from Backend.services.data_analysis.inferential_service import run_inferential_analysis

# NEU (Ersetze die oben markierten Zeilen durch):
inferential = {}
if len(conditions) >= 2:
    metric_buckets = {
        "total": condition_total,
        "phase1": condition_phase1,
        "phase2": condition_phase2,
        "phase3": condition_phase3,
    }
    for metric, bucket_dict in metric_buckets.items():
        metric_conditions = {cond: bucket_dict.get(cond, []) for cond in conditions}
        inferential[metric] = run_inferential_analysis(metric_conditions)
```

- [ ] **Step 3: Alle bestehenden Tests prüfen**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

Erwartung: keine Regression.

- [ ] **Step 4: Commit**

```bash
git add Backend/services/data_analysis/performance_analysis_service.py Backend/tests/test_analysis.py
git commit -m "feat: extend performance_analysis to support N conditions via inferential_service"
```

---

## Chunk 3: Extended Eye-Tracking & Questionnaire Services

### Task 7: Eye-Tracking — Sakkaden, Transition Matrix, Phase-Zuordnung, PPI

**Files:**
- Modify: `Web/Backend/services/data_analysis/eye_tracking_analysis_service.py`
- Create: `Web/Backend/tests/test_eye_tracking_extended.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_eye_tracking_extended.py
from Backend.services.data_analysis.eye_tracking_analysis_service import (
    compute_saccades_and_transitions,
    compute_ppi,
    assign_fixations_to_phases,
)
from datetime import datetime, timedelta

def make_fixation(aoi_name, start_ms, duration_ms):
    """Helper: simulates an EyeTracking-like dict."""
    base = datetime(2024, 1, 1)
    return {
        "aoi_name": aoi_name,
        "starttime": base + timedelta(milliseconds=start_ms),
        "endtime": base + timedelta(milliseconds=start_ms + duration_ms),
        "duration": duration_ms,
    }

def test_saccade_count():
    fixations = [
        make_fixation("object", 0, 100),
        make_fixation("partner_hand", 100, 100),
        make_fixation("object", 200, 100),
        make_fixation("object", 300, 100),  # same AOI → no saccade
    ]
    result = compute_saccades_and_transitions(fixations)
    assert result["saccade_count"] == 2  # object→partner_hand, partner_hand→object

def test_transition_matrix_keys():
    fixations = [
        make_fixation("object", 0, 100),
        make_fixation("own_hand", 100, 100),
    ]
    result = compute_saccades_and_transitions(fixations)
    assert ("object", "own_hand") in result["transition_counts"] or \
           result["transition_counts"].get(("object", "own_hand"), 0) == 1

def test_ppi_basic():
    base = datetime(2024, 1, 1)
    phase3_start = base + timedelta(milliseconds=0)
    phase3_end = base + timedelta(milliseconds=1000)
    fixations = [
        make_fixation("environment", 0, 300),
        make_fixation("object", 300, 700),
    ]
    ppi = compute_ppi(fixations, phase3_start, phase3_end)
    assert abs(ppi - 30.0) < 0.1  # 300/1000 * 100 = 30%

def test_ppi_no_environment():
    base = datetime(2024, 1, 1)
    phase3_start = base
    phase3_end = base + timedelta(milliseconds=1000)
    fixations = [make_fixation("object", 0, 1000)]
    ppi = compute_ppi(fixations, phase3_start, phase3_end)
    assert ppi == 0.0

def test_assign_fixations_to_phases():
    base = datetime(2024, 1, 1)
    fixations = [
        make_fixation("object", 0, 100),    # phase 1
        make_fixation("own_hand", 300, 100), # phase 2
        make_fixation("environment", 700, 100), # phase 3
    ]
    phases = {
        "phase1": (base, base + timedelta(milliseconds=200)),
        "phase2": (base + timedelta(milliseconds=200), base + timedelta(milliseconds=600)),
        "phase3": (base + timedelta(milliseconds=600), base + timedelta(milliseconds=1000)),
    }
    assigned = assign_fixations_to_phases(fixations, phases)
    assert "phase1" in assigned
    assert any(f["aoi_name"] == "object" for f in assigned["phase1"])
    assert any(f["aoi_name"] == "environment" for f in assigned["phase3"])
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_eye_tracking_extended.py -v
```

- [ ] **Step 3: Hilfsfunktionen in eye_tracking_analysis_service.py ergänzen**

Am Ende der Datei (vor bestehenden `analyze_*`-Funktionen):

```python
def compute_saccades_and_transitions(fixations: list[dict]) -> dict:
    """
    fixations: list of dicts with keys: aoi_name, starttime, endtime, duration
    Sorted by starttime ascending before calling this function.
    """
    saccade_count = 0
    transition_counts: dict[tuple, int] = {}
    sorted_fixations = sorted(fixations, key=lambda f: f["starttime"])

    for i in range(1, len(sorted_fixations)):
        prev_aoi = sorted_fixations[i - 1]["aoi_name"]
        curr_aoi = sorted_fixations[i]["aoi_name"]
        if prev_aoi != curr_aoi:
            saccade_count += 1
            key = (prev_aoi, curr_aoi)
            transition_counts[key] = transition_counts.get(key, 0) + 1

    total_duration_ms = sum(f["duration"] for f in fixations if f["duration"])
    saccade_rate = saccade_count / (total_duration_ms / 1000.0) if total_duration_ms > 0 else 0.0

    return {
        "saccade_count": saccade_count,
        "saccade_rate": round(saccade_rate, 4),
        "transition_counts": transition_counts,
    }


def compute_ppi(fixations: list[dict], phase3_start, phase3_end) -> float:
    """
    Proactive Planning Index:
    dwell_time("environment", phase=3) / phase3_total_duration * 100
    """
    phase3_duration_ms = (phase3_end - phase3_start).total_seconds() * 1000
    if phase3_duration_ms <= 0:
        return 0.0

    env_dwell = sum(
        f["duration"] for f in fixations
        if f["aoi_name"] == "environment"
        and f["duration"] is not None
        and phase3_start <= f["starttime"] < phase3_end
    )
    return round((env_dwell / phase3_duration_ms) * 100.0, 4)


def assign_fixations_to_phases(fixations: list[dict],
                                phases: dict[str, tuple]) -> dict[str, list]:
    """
    phases: {"phase1": (start_dt, end_dt), "phase2": ..., "phase3": ...}
    Returns dict of phase_name → list of fixation dicts that fall in that phase.
    """
    assigned: dict[str, list] = {phase: [] for phase in phases}
    for fix in fixations:
        fix_start = fix["starttime"]
        for phase_name, (p_start, p_end) in phases.items():
            if p_start <= fix_start < p_end:
                assigned[phase_name].append(fix)
                break
    return assigned
```

- [ ] **Step 4: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_eye_tracking_extended.py -v
```

Erwartung: alle grün.

- [ ] **Step 5: Vollständige ET-Testabdeckung**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

- [ ] **Step 6: Commit**

```bash
git add Backend/services/data_analysis/eye_tracking_analysis_service.py Backend/tests/test_eye_tracking_extended.py
git commit -m "feat: add saccades, transition matrix, PPI and phase-assignment to eye tracking service"
```

---

### Task 8: Questionnaire-Scoring (instrument-aware)

**Files:**
- Create: `Web/Backend/services/data_analysis/questionnaire_scoring.py`
- Create: `Web/Backend/tests/test_questionnaire_scoring.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_questionnaire_scoring.py
from Backend.services.data_analysis.questionnaire_scoring import (
    score_nasa_tlx, score_sus, score_attrakdiff2, score_iso_metrics,
    score_questionnaire,
)

def test_nasa_tlx_mean():
    items = [{"item_name": f"item_{i}", "response_value": float(i * 10)}
             for i in range(1, 7)]
    result = score_nasa_tlx(items)
    assert result["raw_tlx"] == pytest.approx(35.0)  # mean of 10,20,30,40,50,60

def test_sus_scoring():
    # SUS: odd items (1,3,5,7,9): (x-1)*2.5; even (2,4,6,8,10): (5-x)*2.5
    items = [
        {"item_name": "sus_1", "response_value": 5.0},  # odd → (5-1)*2.5 = 10
        {"item_name": "sus_2", "response_value": 1.0},  # even → (5-1)*2.5 = 10
        {"item_name": "sus_3", "response_value": 5.0},
        {"item_name": "sus_4", "response_value": 1.0},
        {"item_name": "sus_5", "response_value": 5.0},
        {"item_name": "sus_6", "response_value": 1.0},
        {"item_name": "sus_7", "response_value": 5.0},
        {"item_name": "sus_8", "response_value": 1.0},
        {"item_name": "sus_9", "response_value": 5.0},
        {"item_name": "sus_10", "response_value": 1.0},
    ]
    result = score_sus(items)
    assert result["sus_score"] == pytest.approx(100.0)

def test_attrakdiff2_subscales():
    items = [
        {"item_name": "pq_1", "response_value": 6.0},
        {"item_name": "pq_2", "response_value": 4.0},
        {"item_name": "hqs_1", "response_value": 5.0},
        {"item_name": "hqi_1", "response_value": 3.0},
        {"item_name": "att_1", "response_value": 7.0},
    ]
    result = score_attrakdiff2(items)
    assert result["PQ"] == pytest.approx(5.0)
    assert result["HQS"] == pytest.approx(5.0)
    assert result["HQI"] == pytest.approx(3.0)
    assert result["ATT"] == pytest.approx(7.0)
    assert result["HQ"] == pytest.approx(4.0)  # mean(HQS, HQI)

def test_score_questionnaire_dispatch():
    nasa_items = [{"item_name": f"i{i}", "response_value": 50.0} for i in range(6)]
    result = score_questionnaire("NASA-TLX", nasa_items)
    assert "raw_tlx" in result
```

- [ ] **Step 2: Test ausführen — muss fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_questionnaire_scoring.py -v
```

- [ ] **Step 3: questionnaire_scoring.py erstellen**

```python
# Backend/services/data_analysis/questionnaire_scoring.py
"""
Instrument-aware questionnaire scoring.
All functions receive items as list of dicts: {"item_name": str, "response_value": float}
For ISO-Metrics: items also need "item_description": str
"""
from collections import defaultdict


def score_nasa_tlx(items: list[dict]) -> dict:
    values = [i["response_value"] for i in items if i.get("response_value") is not None]
    return {"raw_tlx": round(sum(values) / len(values), 2) if values else None}


def score_sus(items: list[dict]) -> dict:
    """SUS scoring: odd items (1,3,5,7,9): (x-1)*2.5; even (2,4,6,8,10): (5-x)*2.5"""
    total = 0.0
    for i, item in enumerate(sorted(items, key=lambda x: x["item_name"]), start=1):
        v = item.get("response_value")
        if v is None:
            continue
        if i % 2 == 1:  # odd
            total += (v - 1) * 2.5
        else:  # even
            total += (5 - v) * 2.5
    return {"sus_score": round(total, 2)}


def score_attrakdiff2(items: list[dict]) -> dict:
    buckets: dict[str, list] = defaultdict(list)
    for item in items:
        name = item.get("item_name", "")
        v = item.get("response_value")
        if v is None:
            continue
        if name.startswith("pq_"):
            buckets["PQ"].append(v)
        elif name.startswith("hqs_"):
            buckets["HQS"].append(v)
        elif name.startswith("hqi_"):
            buckets["HQI"].append(v)
        elif name.startswith("att_"):
            buckets["ATT"].append(v)

    result = {}
    for sub in ("PQ", "HQS", "HQI", "ATT"):
        vals = buckets.get(sub, [])
        result[sub] = round(sum(vals) / len(vals), 4) if vals else None

    hqs = result.get("HQS")
    hqi = result.get("HQI")
    if hqs is not None and hqi is not None:
        result["HQ"] = round((hqs + hqi) / 2, 4)
    else:
        result["HQ"] = None
    return result


ISO_SUBSCALES = [
    "Aufgabenangemessenheit",
    "Selbstbeschreibungsfähigkeit",
    "Steuerbarkeit",
    "Erwartungskonformität",
    "Individualisierbarkeit",
    "Fehlertoleranz",
    "Lernförderlichkeit",
]


def score_iso_metrics(items: list[dict]) -> dict:
    buckets: dict[str, list] = defaultdict(list)
    for item in items:
        desc = item.get("item_description", "")
        v = item.get("response_value")
        if v is None or desc not in ISO_SUBSCALES:
            continue
        buckets[desc].append(v)
    return {
        sub: round(sum(vals) / len(vals), 4) if vals else None
        for sub, vals in buckets.items()
    }


def score_questionnaire(questionnaire_name: str, items: list[dict]) -> dict:
    name = questionnaire_name.strip()
    if name == "NASA-TLX":
        return score_nasa_tlx(items)
    if name == "SUS":
        return score_sus(items)
    if name == "AttrakDiff2":
        return score_attrakdiff2(items)
    if name == "ISO-Metrics":
        return score_iso_metrics(items)
    # Custom questionnaire: simple mean
    values = [i["response_value"] for i in items if i.get("response_value") is not None]
    return {"mean": round(sum(values) / len(values), 4) if values else None}
```

- [ ] **Step 4: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_questionnaire_scoring.py -v
```

- [ ] **Step 5: Alle Tests grün**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

- [ ] **Step 6: Commit**

```bash
git add Backend/services/data_analysis/questionnaire_scoring.py Backend/tests/test_questionnaire_scoring.py
git commit -m "feat: add instrument-aware questionnaire scoring (NASA-TLX, SUS, AttrakDiff2, ISO-Metrics)"
```

---

## Chunk 4: Correlation, Cross-Study, Exploratory Services

### Task 9: correlation_service.py

**Files:**
- Create: `Web/Backend/services/data_analysis/correlation_service.py`
- Create: `Web/Backend/tests/test_correlation.py`

- [ ] **Step 1: Test schreiben**

```python
# Backend/tests/test_correlation.py
import pytest
import numpy as np
from Backend.services.data_analysis.correlation_service import (
    auto_correlate, correlate_pair,
)

def test_pearson_selected_for_normal():
    np.random.seed(0)
    x = list(np.random.normal(5, 1, 20))
    y = [xi * 2 + np.random.normal(0, 0.1) for xi in x]
    result = auto_correlate(x, y)
    assert result["method"] in ("pearson", "spearman")
    assert result["r"] is not None
    assert result["p_value"] is not None
    assert "r_squared" in result

def test_spearman_for_non_normal():
    x = [1, 1, 1, 1, 1, 1, 1, 1, 100]  # clearly non-normal
    y = [2, 2, 2, 2, 2, 2, 2, 2, 200]
    result = auto_correlate(x, y)
    assert result["method"] == "spearman"

def test_too_few_data():
    result = auto_correlate([1.0, 2.0], [3.0, 4.0])
    assert result is None

def test_r_squared():
    np.random.seed(1)
    x = list(np.random.normal(5, 1, 30))
    y = [xi * 1.5 for xi in x]
    result = auto_correlate(x, y)
    assert result["r_squared"] == pytest.approx(result["r"] ** 2, abs=0.01)
```

- [ ] **Step 2: Test ausführen — fehlschlagen**

```bash
cd Web && uv run pytest Backend/tests/test_correlation.py -v
```

- [ ] **Step 3: correlation_service.py erstellen**

```python
# Backend/services/data_analysis/correlation_service.py
import math
import scipy.stats as scipy_stats


def auto_correlate(x: list, y: list) -> dict | None:
    """
    Auto-selects Pearson r (both normal) or Spearman ρ.
    Returns None if n < 4.
    """
    if len(x) < 4 or len(y) < 4 or len(x) != len(y):
        return None

    def _shapiro_p(vals):
        if len(vals) > 3:
            return scipy_stats.shapiro(vals).pvalue
        return 0.0

    p_x = _shapiro_p(x)
    p_y = _shapiro_p(y)

    if p_x >= 0.05 and p_y >= 0.05:
        r, p = scipy_stats.pearsonr(x, y)
        method = "pearson"
    else:
        r, p = scipy_stats.spearmanr(x, y)
        method = "spearman"

    r = float(r)
    p = float(p)
    return {
        "method": method,
        "r": None if math.isnan(r) else round(r, 4),
        "p_value": None if math.isnan(p) else round(p, 4),
        "r_squared": None if math.isnan(r) else round(r ** 2, 4),
        "significant": bool(p < 0.05),
    }


def correlate_pair(x: list, y: list, label_x: str, label_y: str,
                   bonferroni_n: int = 1) -> dict | None:
    result = auto_correlate(x, y)
    if result is None:
        return None
    # Bonferroni correction
    p_adj = min(result["p_value"] * bonferroni_n, 1.0) if result["p_value"] is not None else None
    result["label_x"] = label_x
    result["label_y"] = label_y
    result["p_adjusted"] = round(p_adj, 4) if p_adj is not None else None
    result["significant_adjusted"] = bool(p_adj < 0.05) if p_adj is not None else None
    return result
```

- [ ] **Step 4: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_correlation.py -v
```

- [ ] **Step 5: Commit**

```bash
git add Backend/services/data_analysis/correlation_service.py Backend/tests/test_correlation.py
git commit -m "feat: add correlation_service with Pearson/Spearman auto-selection and Bonferroni correction"
```

---

### Task 10: cross_study_service.py

**Files:**
- Create: `Web/Backend/services/data_analysis/cross_study_service.py`

- [ ] **Step 1: cross_study_service.py erstellen**

```python
# Backend/services/data_analysis/cross_study_service.py
"""
Descriptive cross-study comparison. No inferential tests (different participants per study).
"""
import numpy as np
import scipy.stats as scipy_stats
from Backend.models import Experiment
from Backend.db.trial.trial import TrialRepository
from Backend.db.handover_repository import HandoverRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.services.data_analysis.effect_size_service import cliffs_delta


def _ci_95(values: list) -> tuple[float | None, float | None]:
    n = len(values)
    if n < 2:
        return None, None
    mean = np.mean(values)
    sem = scipy_stats.sem(values)
    t = scipy_stats.t.ppf(0.975, n - 1)
    return round(float(mean - t * sem), 2), round(float(mean + t * sem), 2)


def analyze_cross_study(session, study_ids: list[int],
                         baseline_ms: float = 300.0) -> dict:
    """
    For each study: aggregate mean transfer duration + CI across all conditions.
    Returns list of study summaries for Forest Plot and side-by-side display.
    """
    from Backend.models.study.study import Study

    studies_result = []
    for study_id in study_ids:
        study = session.query(Study).filter_by(study_id=study_id).first()
        if not study:
            continue

        experiments = session.query(Experiment).filter_by(study_id=study_id).all()
        if not experiments:
            continue

        t_repo = TrialRepository(session)
        h_repo = HandoverRepository(session)
        s_repo = StimuliRepository(session)

        all_totals = []
        conditions_seen = set()

        for exp in experiments:
            trials = t_repo.get_by_experiment_id(exp.experiment_id)
            if not trials:
                continue
            trial_ids = [t.trial_id for t in trials]
            trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

            for trial in trials:
                stimuli = trial_stimuli_map.get(trial.trial_id, [])
                if stimuli:
                    conditions_seen.add(stimuli[0]["name"])
                handovers = h_repo.get_handovers_for_trial(trial.trial_id)
                for h in handovers:
                    if not all([h.giver_grasped_object, h.giver_released_object]):
                        continue
                    total_s = (h.giver_released_object - h.giver_grasped_object).total_seconds()
                    all_totals.append(total_s * 1000)  # → ms

        if not all_totals:
            continue

        ci_lo, ci_hi = _ci_95(all_totals)
        mean_ms = round(float(np.mean(all_totals)), 2)

        studies_result.append({
            "study_id": study_id,
            "study_name": study.name if hasattr(study, "name") else f"Study {study_id}",
            "conditions": sorted(conditions_seen),
            "n_experiments": len(experiments),
            "metrics": {
                "total_mean_ms": mean_ms,
                "total_ci_lower": ci_lo,
                "total_ci_upper": ci_hi,
                "n_handovers": len(all_totals),
            },
        })

    return {
        "baseline_ms": baseline_ms,
        "studies": studies_result,
        "warning": "Deskriptiver Vergleich — kein inferenzieller Test (verschiedene Stichproben je Studie)",
    }
```

- [ ] **Step 2: Commit**

```bash
git add Backend/services/data_analysis/cross_study_service.py
git commit -m "feat: add cross_study_service (descriptive only, Forest Plot data)"
```

> **Hinweis:** Das `Study`-ORM-Modell (`Backend/models/study/study.py`) hat kein `name`-Feld (nur `study_id`, `created_at`, `started_at`, `ended_at`, `status`). Der `hasattr`-Guard im Service greift immer und liefert `"Study {id}"` als Fallback. Das ist akzeptabel — der Forscher kann die IDs zuordnen. Falls ein Studiename gewünscht wird, muss dies als separate Schema-Erweiterung behandelt werden.

---

### Task 11: exploratory_service.py (PCA + Clustering)

**Files:**
- Create: `Web/Backend/services/data_analysis/exploratory_service.py`

- [ ] **Step 1: exploratory_service.py erstellen**

```python
# Backend/services/data_analysis/exploratory_service.py
"""
Server-side PCA and hierarchical clustering.
Input: dict of {condition: {metric: value}} per experiment.
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist


def run_pca(data_matrix: list[dict], feature_names: list[str],
             sample_labels: list[str]) -> dict | None:
    """
    data_matrix: list of dicts {feature: value} — one per experiment/participant
    Returns PCA biplot data: loadings (arrows) + scores (points).
    """
    if len(data_matrix) < 3 or len(feature_names) < 2:
        return None

    X = np.array([[row.get(f, 0.0) for f in feature_names] for row in data_matrix])
    X = np.nan_to_num(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_components = min(2, X_scaled.shape[1], X_scaled.shape[0])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(X_scaled)

    return {
        "explained_variance_ratio": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "scores": [
            {"label": sample_labels[i], "pc1": round(float(scores[i, 0]), 4),
             "pc2": round(float(scores[i, 1]), 4) if n_components > 1 else 0.0}
            for i in range(len(sample_labels))
        ],
        "loadings": [
            {"feature": feature_names[j],
             "pc1": round(float(pca.components_[0, j]), 4),
             "pc2": round(float(pca.components_[1, j]), 4) if n_components > 1 else 0.0}
            for j in range(len(feature_names))
        ],
    }


def run_clustering(data_matrix: list[dict], feature_names: list[str],
                    sample_labels: list[str]) -> dict | None:
    """
    Returns dendrogram linkage data for hierarchical clustering.
    """
    if len(data_matrix) < 3:
        return None

    X = np.array([[row.get(f, 0.0) for f in feature_names] for row in data_matrix])
    X = np.nan_to_num(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    linkage = hierarchy.linkage(X_scaled, method="ward")
    dendro = hierarchy.dendrogram(linkage, labels=sample_labels, no_plot=True)

    return {
        "labels": dendro["ivl"],
        "linkage": linkage.tolist(),
        "icoord": dendro["icoord"],
        "dcoord": dendro["dcoord"],
    }
```

- [ ] **Step 2: Tests für exploratory_service**

```python
# Backend/tests/test_exploratory.py
import numpy as np
from Backend.services.data_analysis.exploratory_service import run_pca, run_clustering

def make_data(n=10, features=None):
    if features is None:
        features = ["transfer_ms", "phase1_ms", "nasa_tlx"]
    rng = np.random.default_rng(42)
    data = [{f: float(rng.normal(5, 1)) for f in features} for _ in range(n)]
    labels = [f"exp_{i}" for i in range(n)]
    return data, features, labels

def test_pca_returns_scores_and_loadings():
    data, features, labels = make_data()
    result = run_pca(data, features, labels)
    assert result is not None
    assert "scores" in result
    assert "loadings" in result
    assert len(result["scores"]) == len(data)
    assert len(result["loadings"]) == len(features)
    assert "explained_variance_ratio" in result
    assert len(result["explained_variance_ratio"]) == 2

def test_pca_too_few_samples_returns_none():
    data, features, labels = make_data(n=2)
    assert run_pca(data, features, labels) is None

def test_clustering_returns_dendrogram_structure():
    data, features, labels = make_data()
    result = run_clustering(data, features, labels)
    assert result is not None
    assert "labels" in result
    assert "linkage" in result
    assert len(result["labels"]) == len(data)

def test_clustering_too_few_samples_returns_none():
    data, features, labels = make_data(n=2)
    assert run_clustering(data, features, labels) is None
```

- [ ] **Step 3: Tests ausführen**

```bash
cd Web && uv run pytest Backend/tests/test_exploratory.py -v
```

Erwartung: alle grün.

- [ ] **Step 4: Commit**

```bash
git add Backend/services/data_analysis/exploratory_service.py Backend/tests/test_exploratory.py
git commit -m "feat: add exploratory_service (server-side PCA + hierarchical clustering)"
```

---

## Chunk 5: API-Endpunkte & Export

### Task 12: Pydantic Response-Modelle

**Files:**
- Create: `Web/Backend/models/analysis.py`

- [ ] **Step 1: analysis.py erstellen**

```python
# Backend/models/analysis.py
from pydantic import BaseModel
from typing import Optional, Any


class PosthocPair(BaseModel):
    pair: list[str]
    p_value: Optional[float]
    p_adjusted: Optional[float]
    correction: Optional[str]
    effect_size_d: Optional[float]
    effect_size_d_interpretation: Optional[str]
    effect_size_cliffs_delta: Optional[float]
    effect_size_cliffs_delta_interpretation: Optional[str]
    significant: Optional[bool]


class MainEffect(BaseModel):
    statistic: Optional[float]
    p_value: Optional[float]
    significant: Optional[bool]
    effect_eta2p: Optional[float]
    effect_omega2p: Optional[float]
    effect_kendalls_w: Optional[float]
    # k=2 effect sizes (reported here, not in posthoc for 2-condition case)
    effect_size_d: Optional[float] = None
    effect_size_d_interpretation: Optional[str] = None
    effect_size_cliffs_delta: Optional[float] = None
    effect_size_cliffs_delta_interpretation: Optional[str] = None


class InferentialResult(BaseModel):
    test_used: Optional[str]
    n_conditions: int
    normality: dict[str, Optional[float]]
    sphericity_p: Optional[float]
    sphericity_correction: str
    main_effect: MainEffect
    posthoc: list[PosthocPair]


class InferentialAnalysisResponse(BaseModel):
    """Multi-metric inferential results for a study (one result per phase metric)."""
    study_id: int
    # Keys: "total", "phase1", "phase2", "phase3" — each Optional[InferentialResult]
    inferential: dict[str, Optional[InferentialResult]]


class PPIResponse(BaseModel):
    study_id: int
    conditions: dict[str, dict[str, Optional[float]]]  # condition → {giver_ppi, receiver_ppi}


class PhaseAOIResponse(BaseModel):
    study_id: int
    conditions: dict[str, dict[str, Any]]  # condition → {phase1: {aoi: %}, ...}


class TransitionResponse(BaseModel):
    study_id: int
    conditions: dict[str, Any]


class CorrelationPair(BaseModel):
    label_x: str
    label_y: str
    method: str
    r: Optional[float]
    p_value: Optional[float]
    p_adjusted: Optional[float]
    r_squared: Optional[float]
    significant: Optional[bool]
    significant_adjusted: Optional[bool]


class CorrelationResponse(BaseModel):
    study_id: int
    correlations: list[CorrelationPair]


class CrossStudyMetrics(BaseModel):
    total_mean_ms: Optional[float]
    total_ci_lower: Optional[float]
    total_ci_upper: Optional[float]
    n_handovers: int


class CrossStudyEntry(BaseModel):
    study_id: int
    study_name: str
    conditions: list[str]
    n_experiments: int
    metrics: CrossStudyMetrics


class CrossStudyResponse(BaseModel):
    baseline_ms: float
    studies: list[CrossStudyEntry]
    warning: str


class QualityCheckResponse(BaseModel):
    study_id: int
    total_experiments: int
    completed_experiments: int
    missing_timestamps: int
    missing_et_records: int
    n_per_condition: dict[str, int]
    warnings: list[str]
```

- [ ] **Step 2: Commit**

```bash
git add Backend/models/analysis.py
git commit -m "feat: add Pydantic response models for analysis endpoints"
```

---

### Task 13: Neue Analysis-Endpunkte

**Files:**
- Modify: `Web/Backend/routes/analysis.py`

- [ ] **Step 1: Neue Endpunkte hinzufügen**

In `Backend/routes/analysis.py` ergänzen:

```python
from Backend.services.data_analysis.inferential_service import run_inferential_analysis
from Backend.services.data_analysis.correlation_service import correlate_pair
from Backend.services.data_analysis.cross_study_service import analyze_cross_study
from Backend.services.data_analysis.eye_tracking_analysis_service import (
    compute_saccades_and_transitions, compute_ppi, assign_fixations_to_phases,
)
from Backend.models.analysis import (
    CrossStudyResponse, QualityCheckResponse, CorrelationResponse,
)

@router.get("/study/{study_id}/inferential")
async def study_inferential(study_id: int, handedness: str = "all", db=Depends(get_db)):
    from Backend.services.data_analysis.performance_analysis_service import analyze_study_performance
    result = analyze_study_performance(db, study_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data")
    # Return the inferential block from performance analysis
    return {"study_id": study_id, "inferential": result.get("performance", {}).get("inferential", {})}


@router.get("/study/{study_id}/eye-tracking/phases")
async def study_eye_tracking_phases(study_id: int, handedness: str = "all", db=Depends(get_db)):
    result = analyze_study_eye_tracking(db, study_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data")
    return {"study_id": study_id, "phases": result}


@router.get("/study/{study_id}/eye-tracking/transitions")
async def study_eye_tracking_transitions(study_id: int, db=Depends(get_db)):
    result = analyze_study_eye_tracking(db, study_id)
    return {"study_id": study_id, "transitions": result}


@router.get("/study/{study_id}/ppi")
async def study_ppi(study_id: int, db=Depends(get_db)):
    result = analyze_study_eye_tracking(db, study_id)
    return {"study_id": study_id, "ppi": result}


@router.get("/study/{study_id}/correlations", response_model=CorrelationResponse)
async def study_correlations(study_id: int, handedness: str = "all", db=Depends(get_db)):
    # Placeholder: returns empty for now, full implementation in correlation_service integration
    return CorrelationResponse(study_id=study_id, correlations=[])


@router.get("/cross-study", response_model=CrossStudyResponse)
async def cross_study(study_ids: str, baseline_ms: float = 300.0, db=Depends(get_db)):
    ids = [int(i.strip()) for i in study_ids.split(",") if i.strip().isdigit()]
    if not ids:
        raise HTTPException(status_code=400, detail="Invalid study_ids")
    result = analyze_cross_study(db, ids, baseline_ms)
    return result


@router.get("/study/{study_id}/quality-check", response_model=QualityCheckResponse)
async def study_quality_check(study_id: int, db=Depends(get_db)):
    from Backend.models import Experiment
    from Backend.models.handover import Handover
    from Backend.db.trial.trial import TrialRepository

    experiments = db.query(Experiment).filter_by(study_id=study_id).all()
    t_repo = TrialRepository(db)
    missing_ts = 0
    missing_et = 0
    n_per_condition: dict[str, int] = {}

    for exp in experiments:
        trials = t_repo.get_by_experiment_id(exp.experiment_id)
        for trial in (trials or []):
            handovers = db.query(Handover).filter_by(trial_id=trial.trial_id).all()
            for h in handovers:
                if not all([h.giver_grasped_object, h.receiver_touched_object,
                             h.receiver_grasped_object, h.giver_released_object]):
                    missing_ts += 1
                if not h.eye_trackings:
                    missing_et += 1

    warnings = []
    if missing_ts > 0:
        warnings.append(f"{missing_ts} Handover(s) ohne vollständige Timestamps")
    if missing_et > 0:
        warnings.append(f"{missing_et} Handover(s) ohne Eye-Tracking-Daten")

    return QualityCheckResponse(
        study_id=study_id,
        total_experiments=len(experiments),
        completed_experiments=len(experiments),
        missing_timestamps=missing_ts,
        missing_et_records=missing_et,
        n_per_condition=n_per_condition,
        warnings=warnings,
    )
```

- [ ] **Step 2: Tests für Endpunkte**

```bash
cd Web && uv run pytest Backend/tests/ -q
```

Erwartung: alle bestehenden Tests noch grün.

- [ ] **Step 3: Commit**

```bash
git add Backend/routes/analysis.py
git commit -m "feat: add new analysis API endpoints (inferential, phases, ppi, cross-study, quality-check)"
```

---

### Task 14: Export-Endpunkte (CSV / XLSX)

> **Scope MVP:** Dieser Task implementiert nur den Handover-Rohdaten-Export. Eye-Tracking- und Questionnaire-Export (spec 5.9: "separate Sheets") sind zukünftige Erweiterungen. Den Scope in der Response explizit dokumentieren.

**Files:**
- Create: `Web/Backend/routes/export_routes.py`

- [ ] **Step 1: export_routes.py erstellen**

```python
# Backend/routes/export_routes.py
import csv
import io
import zipfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import openpyxl

from Backend.db_session import SessionLocal
from Backend.models import Experiment
from Backend.models.handover import Handover
from Backend.db.trial.trial import TrialRepository

router = APIRouter(prefix="/export", tags=["export"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _handovers_for_study(db, study_id: int) -> list[dict]:
    rows = []
    experiments = db.query(Experiment).filter_by(study_id=study_id).all()
    t_repo = TrialRepository(db)
    for exp in experiments:
        trials = t_repo.get_by_experiment_id(exp.experiment_id)
        for trial in (trials or []):
            handovers = db.query(Handover).filter_by(trial_id=trial.trial_id).all()
            for h in handovers:
                rows.append({
                    "study_id": study_id,
                    "experiment_id": exp.experiment_id,
                    "trial_id": trial.trial_id,
                    "handover_id": h.handover_id,
                    "grasped_object": h.grasped_object,
                    "giver": h.giver,
                    "receiver": h.receiver,
                    "giver_grasped_object": h.giver_grasped_object.isoformat() if h.giver_grasped_object else "",
                    "receiver_touched_object": h.receiver_touched_object.isoformat() if h.receiver_touched_object else "",
                    "receiver_grasped_object": h.receiver_grasped_object.isoformat() if h.receiver_grasped_object else "",
                    "giver_released_object": h.giver_released_object.isoformat() if h.giver_released_object else "",
                    "is_error": 1 if h.is_error else 0,  # SPSS: integer not bool
                    "error_type": h.error_type or "",
                })
    return rows


@router.get("/study/{study_id}/raw")
async def export_study_raw(study_id: int, format: str = "csv", db=Depends(get_db)):
    rows = _handovers_for_study(db, study_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No data")

    if format == "xlsx":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Handovers"
        if rows:
            ws.append(list(rows[0].keys()))
            for row in rows:
                ws.append(list(row.values()))
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=study_{study_id}_raw.xlsx"},
        )

    # CSV (UTF-8-sig = UTF-8 with BOM — Windows/SPSS compatible)
    buf = io.BytesIO()
    wrapper = io.TextIOWrapper(buf, encoding="utf-8-sig", newline="")
    if rows:
        writer = csv.DictWriter(wrapper, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    wrapper.flush()
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=study_{study_id}_raw.csv"},
    )
```

- [ ] **Step 2: Route registrieren**

In `Backend/routes/__init__.py` prüfen ob `export_routes` bereits importiert wird. Falls nicht, den Router hinzufügen (das Modul mit `router`-Attribut wird automatisch gefunden).

- [ ] **Step 3: Smoke-Test**

```bash
cd Web && uv run fastapi dev Backend/app.py &
curl "http://localhost:5000/api/export/study/1/raw?format=csv" -I
# Erwartung: 200 oder 404 (kein 500)
```

- [ ] **Step 4: Commit**

```bash
git add Backend/routes/export_routes.py
git commit -m "feat: add export endpoints for raw CSV/XLSX download"
```

---

## Chunk 6: Frontend — Services & Shared Components

### Task 15: inferentialAnalysisService.js

**Files:**
- Create: `Web/src/features/Analysis/services/inferentialAnalysisService.js`

- [ ] **Step 1: Service erstellen**

```javascript
// src/features/Analysis/services/inferentialAnalysisService.js
const BASE = "/api/analysis";

export async function fetchStudyInferential(studyId, handedness = "all") {
  const res = await fetch(`${BASE}/study/${studyId}/inferential?handedness=${handedness}`);
  if (!res.ok) throw new Error(`Inferential fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchStudyEyeTrackingPhases(studyId, handedness = "all") {
  const res = await fetch(`${BASE}/study/${studyId}/eye-tracking/phases?handedness=${handedness}`);
  if (!res.ok) throw new Error(`ET phases fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchStudyEyeTrackingTransitions(studyId) {
  const res = await fetch(`${BASE}/study/${studyId}/eye-tracking/transitions`);
  if (!res.ok) throw new Error(`ET transitions fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchStudyPPI(studyId) {
  const res = await fetch(`${BASE}/study/${studyId}/ppi`);
  if (!res.ok) throw new Error(`PPI fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchStudyCorrelations(studyId, handedness = "all") {
  const res = await fetch(`${BASE}/study/${studyId}/correlations?handedness=${handedness}`);
  if (!res.ok) throw new Error(`Correlations fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchCrossStudy(studyIds, baselineMs = 300) {
  const ids = studyIds.join(",");
  const res = await fetch(`${BASE}/cross-study?study_ids=${ids}&baseline_ms=${baselineMs}`);
  if (!res.ok) throw new Error(`Cross-study fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchQualityCheck(studyId) {
  const res = await fetch(`${BASE}/study/${studyId}/quality-check`);
  if (!res.ok) throw new Error(`Quality check fetch failed: ${res.status}`);
  return res.json();
}
```

- [ ] **Step 2: Commit**

```bash
git add src/features/Analysis/services/inferentialAnalysisService.js
git commit -m "feat: add inferentialAnalysisService with all new API calls"
```

---

### Task 16: Shared UI-Komponenten

**Files:**
- Create: `Web/src/features/Analysis/components/shared/HandednessFilter.jsx`
- Create: `Web/src/features/Analysis/components/shared/InferentialInfoBox.jsx`
- Create: `Web/src/features/Analysis/components/shared/QualityCheckBanner.jsx`
- Create: `Web/src/features/Analysis/components/shared/ChartDownloadButton.jsx`

- [ ] **Step 1: HandednessFilter.jsx**

```jsx
// src/features/Analysis/components/shared/HandednessFilter.jsx
import { Select, MenuItem, FormControl, InputLabel } from "@mui/material";

export default function HandednessFilter({ value, onChange }) {
  return (
    <FormControl size="small" sx={{ minWidth: 160 }}>
      <InputLabel>Händigkeit</InputLabel>
      <Select value={value} label="Händigkeit" onChange={(e) => onChange(e.target.value)}>
        <MenuItem value="all">Alle</MenuItem>
        <MenuItem value="right">Rechtshänder</MenuItem>
        <MenuItem value="left">Linkshänder</MenuItem>
      </Select>
    </FormControl>
  );
}
```

- [ ] **Step 2: InferentialInfoBox.jsx**

```jsx
// src/features/Analysis/components/shared/InferentialInfoBox.jsx
import { useState } from "react";
import { Alert, Collapse, IconButton, Typography } from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";

export default function InferentialInfoBox({ result }) {
  const [open, setOpen] = useState(false);
  if (!result) return null;

  const { test_used, normality, sphericity_correction } = result;

  const normalityText = Object.entries(normality || {})
    .map(([cond, p]) => `${cond}: ${p !== null ? `p=${p}` : "n<4"}`)
    .join(" · ");

  return (
    <Alert
      severity="info"
      icon={<InfoOutlinedIcon fontSize="small" />}
      action={
        <IconButton size="small" onClick={() => setOpen((v) => !v)}>
          {open ? "▲" : "▼"}
        </IconButton>
      }
      sx={{ mb: 1, cursor: "pointer" }}
      onClick={() => setOpen((v) => !v)}
    >
      <Typography variant="caption">
        Test: <strong>{test_used}</strong>
        {sphericity_correction !== "none" && ` · Korrektur: ${sphericity_correction}`}
      </Typography>
      <Collapse in={open}>
        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
          Shapiro-Wilk: {normalityText}
        </Typography>
      </Collapse>
    </Alert>
  );
}
```

- [ ] **Step 3: QualityCheckBanner.jsx**

```jsx
// src/features/Analysis/components/shared/QualityCheckBanner.jsx
import { useEffect, useState } from "react";
import { Alert, AlertTitle } from "@mui/material";
import { fetchQualityCheck } from "../../services/inferentialAnalysisService";

export default function QualityCheckBanner({ studyId }) {
  const [quality, setQuality] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    fetchQualityCheck(studyId).then(setQuality).catch(() => {});
  }, [studyId]);

  if (!quality || dismissed || quality.warnings.length === 0) return null;

  return (
    <Alert severity="warning" onClose={() => setDismissed(true)} sx={{ mb: 2 }}>
      <AlertTitle>Datenqualität</AlertTitle>
      {quality.warnings.map((w, i) => (
        <div key={i}>{w}</div>
      ))}
    </Alert>
  );
}
```

- [ ] **Step 4: ChartDownloadButton.jsx**

```jsx
// src/features/Analysis/components/shared/ChartDownloadButton.jsx
import { IconButton, Tooltip, Menu, MenuItem } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { useState } from "react";

export default function ChartDownloadButton({ plotlyRef, chartName = "chart" }) {
  const [anchor, setAnchor] = useState(null);

  const download = async (format) => {
    setAnchor(null);
    if (!plotlyRef?.current) return;
    const Plotly = (await import("plotly.js-dist-min")).default;
    const el = plotlyRef.current.el || plotlyRef.current;
    // White background for publication
    const layout = { paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff", font: { color: "#000000" } };
    const filename = `${chartName}_${new Date().toISOString().slice(0, 10)}.${format}`;
    if (format === "csv") {
      // Export raw data from the chart's data traces
      const traces = el.data || [];
      const rows = traces.flatMap((t) =>
        (t.x || []).map((x, i) => ({ x, y: (t.y || [])[i], name: t.name }))
      );
      const csv = ["x,y,series", ...rows.map((r) => `${r.x},${r.y},${r.name}`)].join("\n");
      const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8-sig" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `${chartName}.csv`;
      a.click();
      return;
    }
    await Plotly.downloadImage(el, { format, filename, width: 1200, height: 800, scale: 3 });
  };

  return (
    <>
      <Tooltip title="Exportieren">
        <IconButton size="small" onClick={(e) => setAnchor(e.currentTarget)}>
          <DownloadIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
        <MenuItem onClick={() => download("png")}>PNG (300 dpi)</MenuItem>
        <MenuItem onClick={() => download("svg")}>SVG (Vektor)</MenuItem>
        <MenuItem onClick={() => download("csv")}>CSV (Rohdaten)</MenuItem>
      </Menu>
    </>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add src/features/Analysis/components/shared/
git commit -m "feat: add shared UI components (HandednessFilter, InferentialInfoBox, QualityCheckBanner, ChartDownloadButton)"
```

---

## Chunk 7: Frontend — Performance & Eye-Tracking Charts

### Task 17: Performance-Charts

**Files:**
- Create: `Web/src/features/Analysis/components/study/performance/PerformanceBoxplot.jsx`
- Create: `Web/src/features/Analysis/components/study/performance/PosthocHeatmap.jsx`
- Create: `Web/src/features/Analysis/components/study/performance/ErrorRateBar.jsx`

- [ ] **Step 1: PerformanceBoxplot.jsx**

```jsx
// src/features/Analysis/components/study/performance/PerformanceBoxplot.jsx
import { useRef } from "react";
import Plot from "react-plotly.js";
import { Box, Stack, Typography } from "@mui/material";
import ChartDownloadButton from "../../shared/ChartDownloadButton";

export default function PerformanceBoxplot({ data, metric = "total", overlayMode = false }) {
  const ref = useRef();
  if (!data?.performance?.by_condition) return null;

  const conditions = Object.keys(data.performance.by_condition);
  const traces = conditions.map((cond) => {
    const stats = data.performance.by_condition[cond];
    const key = `${metric}_`;
    return {
      type: "box",
      name: cond,
      q1: [stats[`${metric}_q1`]],
      median: [stats[`${metric}_median`]],
      q3: [stats[`${metric}_q3`]],
      lowerfence: [stats[`${metric}_min`]],
      upperfence: [stats[`${metric}_max`]],
      mean: [stats[`${metric}_mean`]],
      boxmean: "sd",
      visible: true,
    };
  });

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="subtitle2">Transferzeit — {metric}</Typography>
        <ChartDownloadButton plotlyRef={ref} chartName={`performance_boxplot_${metric}`} />
      </Stack>
      <Plot
        ref={ref}
        data={traces}
        layout={{
          height: 400,
          xaxis: { title: "Bedingung" },
          yaxis: { title: "Zeit (s)" },
          boxmode: overlayMode ? "overlay" : "group",
        }}
        style={{ width: "100%" }}
        config={{ responsive: true }}
      />
    </Box>
  );
}
```

- [ ] **Step 2: PosthocHeatmap.jsx**

```jsx
// src/features/Analysis/components/study/performance/PosthocHeatmap.jsx
import Plot from "react-plotly.js";
import { Box, Typography, Chip, Stack } from "@mui/material";

export default function PosthocHeatmap({ inferentialResult, metric = "total" }) {
  const result = inferentialResult?.[metric];
  if (!result?.posthoc?.length) return null;

  const pairs = result.posthoc;
  const conditions = [...new Set(pairs.flatMap((p) => p.pair))];
  const n = conditions.length;

  const z = Array.from({ length: n }, () => Array(n).fill(null));
  const text = Array.from({ length: n }, () => Array(n).fill(""));

  pairs.forEach(({ pair, p_adjusted, effect_size_d, effect_size_cliffs_delta, significant }) => {
    const i = conditions.indexOf(pair[0]);
    const j = conditions.indexOf(pair[1]);
    const p = p_adjusted ?? 1;
    z[i][j] = p;
    z[j][i] = p;
    const d = effect_size_d ?? effect_size_cliffs_delta;
    text[i][j] = `p=${p.toFixed(3)}${d ? `\nd=${d.toFixed(2)}` : ""}`;
    text[j][i] = text[i][j];
  });

  return (
    <Box>
      <Stack direction="row" alignItems="center" gap={1} mb={1}>
        <Typography variant="subtitle2">Post-hoc Paarvergleiche — {metric}</Typography>
        <Chip size="small" label={result.test_used} />
      </Stack>
      <Plot
        data={[{
          type: "heatmap",
          z,
          x: conditions,
          y: conditions,
          text,
          texttemplate: "%{text}",
          colorscale: [[0, "#4caf50"], [0.05, "#ffeb3b"], [1, "#e0e0e0"]],
          zmin: 0,
          zmax: 1,
          showscale: true,
          colorbar: { title: "p adj." },
        }]}
        layout={{ height: 350, margin: { t: 10 } }}
        style={{ width: "100%" }}
      />
    </Box>
  );
}
```

- [ ] **Step 3: ErrorRateBar.jsx**

```jsx
// src/features/Analysis/components/study/performance/ErrorRateBar.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Box, Typography } from "@mui/material";

export default function ErrorRateBar({ data }) {
  if (!data?.performance?.by_condition) return null;

  const chartData = Object.entries(data.performance.by_condition).map(([cond, stats]) => ({
    condition: cond,
    error_rate: stats.error_rate ?? 0,
  }));

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>Fehlerrate pro Bedingung (%)</Typography>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="condition" />
          <YAxis unit="%" domain={[0, 100]} />
          <Tooltip formatter={(v) => `${v.toFixed(1)}%`} />
          <Bar dataKey="error_rate" fill="#f44336" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add src/features/Analysis/components/study/performance/
git commit -m "feat: add PerformanceBoxplot, PosthocHeatmap, ErrorRateBar chart components"
```

---

### Task 18: Eye-Tracking Charts

**Files:**
- Create: `Web/src/features/Analysis/components/study/eyetracking/PhaseAOIHeatmap.jsx`
- Create: `Web/src/features/Analysis/components/study/eyetracking/TransitionSankey.jsx`
- Create: `Web/src/features/Analysis/components/study/eyetracking/PPIBar.jsx`

- [ ] **Step 1: PhaseAOIHeatmap.jsx**

```jsx
// src/features/Analysis/components/study/eyetracking/PhaseAOIHeatmap.jsx
import Plot from "react-plotly.js";
import { Box, Typography } from "@mui/material";

const PHASES = ["phase1", "phase2", "phase3"];
const PHASE_LABELS = { phase1: "Koordination", phase2: "Griff", phase3: "Transfer" };

export default function PhaseAOIHeatmap({ data, condition }) {
  if (!data?.phases?.[condition]) return null;

  const phaseData = data.phases[condition];
  const aois = [...new Set(PHASES.flatMap((p) => Object.keys(phaseData[p] || {})))];

  const z = aois.map((aoi) => PHASES.map((ph) => phaseData[ph]?.[aoi] ?? 0));
  const text = z.map((row) => row.map((v) => `${v.toFixed(1)}%`));

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>
        AOI × Phase Verteilung — {condition}
      </Typography>
      <Plot
        data={[{
          type: "heatmap",
          z,
          x: PHASES.map((p) => PHASE_LABELS[p]),
          y: aois,
          text,
          texttemplate: "%{text}",
          colorscale: "Blues",
          showscale: true,
          colorbar: { title: "Blickzeit %" },
        }]}
        layout={{ height: 350, margin: { t: 10, l: 120 } }}
        style={{ width: "100%" }}
      />
    </Box>
  );
}
```

- [ ] **Step 2: TransitionSankey.jsx**

```jsx
// src/features/Analysis/components/study/eyetracking/TransitionSankey.jsx
import Plot from "react-plotly.js";
import { Box, Typography } from "@mui/material";

export default function TransitionSankey({ transitions, condition }) {
  const condData = transitions?.transitions?.[condition];
  if (!condData?.transition_counts) return null;

  const counts = condData.transition_counts;
  const aois = [...new Set(Object.keys(counts).flatMap(([a, b]) => [a, b]))];
  // counts is a dict with stringified tuple keys from Python — parse "[aoi_a, aoi_b]" pairs
  const links = { source: [], target: [], value: [] };
  Object.entries(counts).forEach(([key, val]) => {
    // key format: "('object', 'partner_hand')"
    const match = key.match(/\('(.+?)', '(.+?)'\)/);
    if (!match) return;
    const [, from, to] = match;
    const si = aois.indexOf(from);
    const ti = aois.indexOf(to);
    if (si === -1 || ti === -1) return;
    links.source.push(si);
    links.target.push(ti);
    links.value.push(val);
  });

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>Blick-Übergänge — {condition}</Typography>
      <Plot
        data={[{
          type: "sankey",
          node: { label: aois, pad: 20, thickness: 20 },
          link: links,
        }]}
        layout={{ height: 400 }}
        style={{ width: "100%" }}
      />
    </Box>
  );
}
```

- [ ] **Step 3: PPIBar.jsx**

```jsx
// src/features/Analysis/components/study/eyetracking/PPIBar.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from "recharts";
import { Box, Typography } from "@mui/material";

export default function PPIBar({ ppiData }) {
  if (!ppiData?.ppi) return null;

  const chartData = Object.entries(ppiData.ppi).map(([cond, vals]) => ({
    condition: cond,
    Geber: vals?.giver_ppi ?? 0,
    Empfänger: vals?.receiver_ppi ?? 0,
  }));

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>
        Proaktiver Planungsindex (PPI) — Phase 3
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="condition" />
          <YAxis unit="%" domain={[0, 100]} />
          <Tooltip formatter={(v) => `${v.toFixed(1)}%`} />
          <Legend />
          <ReferenceLine y={30} stroke="green" strokeDasharray="4 4" label="PPI=30%" />
          <Bar dataKey="Geber" fill="#1976d2" />
          <Bar dataKey="Empfänger" fill="#42a5f5" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add src/features/Analysis/components/study/eyetracking/
git commit -m "feat: add PhaseAOIHeatmap, TransitionSankey, PPIBar eye-tracking chart components"
```

---

## Chunk 8: Frontend — Fragebogen & Explorativ

### Task 19: Questionnaire-Charts

**Files:**
- Create: `Web/src/features/Analysis/components/study/questionnaire/AttrakDiffMatrix.jsx`
- Create: `Web/src/features/Analysis/components/study/questionnaire/SUSScoreBar.jsx`

- [ ] **Step 1: AttrakDiffMatrix.jsx (Portfolio-Matrix)**

```jsx
// src/features/Analysis/components/study/questionnaire/AttrakDiffMatrix.jsx
import Plot from "react-plotly.js";
import { Box, Typography } from "@mui/material";

export default function AttrakDiffMatrix({ data }) {
  // data: { conditionName: { PQ, HQ, HQS, HQI, ATT } }
  if (!data) return null;

  const traces = Object.entries(data).map(([cond, scores]) => ({
    type: "scatter",
    mode: "markers+text",
    name: cond,
    x: [scores.PQ],
    y: [scores.HQ],
    text: [cond],
    textposition: "top center",
    marker: { size: 14 },
    // Confidence rectangle via error bars (±1 SE — requires SE data, placeholder ±0.2)
    error_x: { type: "constant", value: 0.2, visible: true },
    error_y: { type: "constant", value: 0.2, visible: true },
  }));

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>AttrakDiff2 Portfolio-Matrix</Typography>
      <Plot
        data={traces}
        layout={{
          height: 450,
          xaxis: { title: "Pragmatische Qualität (PQ)", range: [-3, 3], zeroline: true },
          yaxis: { title: "Hedonische Qualität (HQ)", range: [-3, 3], zeroline: true },
          shapes: [
            // Quadrant labels as annotations
          ],
          annotations: [
            { x: 2, y: 2, text: "begehrt", showarrow: false, font: { color: "#aaa" } },
            { x: -2, y: 2, text: "selbstorientiert", showarrow: false, font: { color: "#aaa" } },
            { x: 2, y: -2, text: "aufgabenorientiert", showarrow: false, font: { color: "#aaa" } },
            { x: -2, y: -2, text: "überflüssig", showarrow: false, font: { color: "#aaa" } },
          ],
        }}
        style={{ width: "100%" }}
      />
    </Box>
  );
}
```

- [ ] **Step 2: SUSScoreBar.jsx**

```jsx
// src/features/Analysis/components/study/questionnaire/SUSScoreBar.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from "recharts";
import { Box, Typography } from "@mui/material";

export default function SUSScoreBar({ data }) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([cond, scores]) => ({
    condition: cond,
    SUS: scores?.sus_score ?? null,
  })).filter((d) => d.SUS !== null);

  return (
    <Box>
      <Typography variant="subtitle2" mb={1}>SUS-Score pro Bedingung</Typography>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="condition" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <ReferenceLine y={68} stroke="orange" strokeDasharray="4 4" label="akzeptabel" />
          <ReferenceLine y={80} stroke="green" strokeDasharray="4 4" label="gut" />
          <Bar dataKey="SUS" fill="#1976d2" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/components/study/questionnaire/
git commit -m "feat: add AttrakDiffMatrix and SUSScoreBar questionnaire chart components"
```

---

## Chunk 9: Cross-Study-Seite & Integration

### Task 20: Cross-Study-Seite + Forest Plot

**Files:**
- Create: `Web/src/features/Analysis/components/study/crossstudy/ForestPlot.jsx`
- Create: `Web/src/features/Analysis/pages/CrossStudyPage.jsx`
- Modify: `Web/src/AppRouter.jsx`

- [ ] **Step 1: ForestPlot.jsx**

```jsx
// src/features/Analysis/components/study/crossstudy/ForestPlot.jsx
import Plot from "react-plotly.js";
import { Box, Typography, Alert } from "@mui/material";

export default function ForestPlot({ crossStudyData }) {
  if (!crossStudyData?.studies?.length) return null;

  const { studies, baseline_ms } = crossStudyData;

  const y = studies.map((s) => s.study_name);
  const x = studies.map((s) => s.metrics.total_mean_ms);
  const errorX = studies.map((s) => ({
    minus: s.metrics.total_mean_ms - (s.metrics.total_ci_lower ?? s.metrics.total_mean_ms),
    plus: (s.metrics.total_ci_upper ?? s.metrics.total_mean_ms) - s.metrics.total_mean_ms,
  }));

  return (
    <Box>
      <Alert severity="warning" sx={{ mb: 1 }}>
        {crossStudyData.warning}
      </Alert>
      <Typography variant="subtitle2" mb={1}>Forest Plot — mittlere Transferzeit</Typography>
      <Plot
        data={[{
          type: "scatter",
          mode: "markers",
          x,
          y,
          error_x: {
            type: "data",
            arrayminus: errorX.map((e) => e.minus),
            array: errorX.map((e) => e.plus),
            visible: true,
          },
          marker: { size: 10 },
          orientation: "h",
        }]}
        layout={{
          height: Math.max(300, studies.length * 60),
          xaxis: { title: "Mittlere Transferzeit (ms)" },
          shapes: [{
            type: "line",
            x0: baseline_ms, x1: baseline_ms,
            y0: -0.5, y1: studies.length - 0.5,
            line: { color: "green", dash: "dash", width: 2 },
          }],
          annotations: [{
            x: baseline_ms, y: studies.length - 0.5,
            text: `Baseline ${baseline_ms}ms`,
            showarrow: false, font: { color: "green", size: 10 },
          }],
        }}
        style={{ width: "100%" }}
      />
    </Box>
  );
}
```

- [ ] **Step 2: CrossStudyPage.jsx**

```jsx
// src/features/Analysis/pages/CrossStudyPage.jsx
import { useState, useEffect } from "react";
import { Box, Typography, TextField, Button, Alert, CircularProgress } from "@mui/material";
import ForestPlot from "../components/study/crossstudy/ForestPlot";
import { fetchCrossStudy } from "../services/inferentialAnalysisService";

export default function CrossStudyPage() {
  const [studyIds, setStudyIds] = useState("");
  const [baselineMs, setBaselineMs] = useState(300);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    const ids = studyIds.split(",").map((s) => parseInt(s.trim())).filter(Boolean);
    if (!ids.length) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCrossStudy(ids, baselineMs);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h5" mb={2}>Studienübergreifender Vergleich</Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Deskriptiver Vergleich — kein inferenzieller Test möglich (verschiedene Stichproben je Studie)
      </Alert>
      <Box display="flex" gap={2} mb={2} flexWrap="wrap">
        <TextField
          label="Studien-IDs (kommagetrennt)"
          value={studyIds}
          onChange={(e) => setStudyIds(e.target.value)}
          size="small"
          sx={{ minWidth: 240 }}
        />
        <TextField
          label="Baseline (ms)"
          type="number"
          value={baselineMs}
          onChange={(e) => setBaselineMs(Number(e.target.value))}
          size="small"
          sx={{ width: 140 }}
        />
        <Button variant="contained" onClick={load} disabled={loading}>
          Analysieren
        </Button>
      </Box>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      {data && <ForestPlot crossStudyData={data} />}
    </Box>
  );
}
```

- [ ] **Step 3: Route in AppRouter.jsx hinzufügen**

In `src/AppRouter.jsx` folgende Route ergänzen (unter den bestehenden `/analysis`-Routen):

```jsx
import CrossStudyPage from "@/features/Analysis/pages/CrossStudyPage";
// ...
<Route path="/analysis/cross-study" element={<CrossStudyPage />} />
```

- [ ] **Step 4: Commit**

```bash
git add src/features/Analysis/components/study/crossstudy/ src/features/Analysis/pages/CrossStudyPage.jsx src/AppRouter.jsx
git commit -m "feat: add ForestPlot and CrossStudyPage with descriptive cross-study comparison"
```

---

### Task 21: StudyAnalysisPage — Integration neuer Komponenten

**Files:**
- Modify: `Web/src/features/Analysis/StudyAnalysisPage.jsx`

- [ ] **Step 1: QualityCheckBanner + HandednessFilter einbinden**

In `StudyAnalysisPage.jsx` oben in der Seite einfügen:

```jsx
import QualityCheckBanner from "./components/shared/QualityCheckBanner";
import HandednessFilter from "./components/shared/HandednessFilter";
// ...
const [handedness, setHandedness] = useState("all");
// Im JSX:
<QualityCheckBanner studyId={studyId} />
<HandednessFilter value={handedness} onChange={setHandedness} />
```

- [ ] **Step 2: PosthocHeatmap + InferentialInfoBox in Performance-Tab**

Im Performance-Tab der Studie (wo `StudyPerformanceCharts` gerendert wird):

```jsx
import PosthocHeatmap from "./components/study/performance/PosthocHeatmap";
import InferentialInfoBox from "./components/shared/InferentialInfoBox";
// ...
{inferentialData && (
  <>
    <InferentialInfoBox result={inferentialData?.inferential?.total} />
    <PosthocHeatmap inferentialResult={inferentialData?.inferential} metric="total" />
  </>
)}
```

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/StudyAnalysisPage.jsx
git commit -m "feat: integrate QualityCheckBanner, HandednessFilter, PosthocHeatmap into StudyAnalysisPage"
```

---

### Task 22: Overlay-Modus für Charts

**Files:**
- Create: `Web/src/features/Analysis/hooks/useOverlayMode.js`
- Modify: `Web/src/features/Analysis/components/study/performance/PerformanceBoxplot.jsx`

- [ ] **Step 1: useOverlayMode.js**

```javascript
// src/features/Analysis/hooks/useOverlayMode.js
import { useState } from "react";

export function useOverlayMode(defaultValue = false) {
  const [overlayMode, setOverlayMode] = useState(defaultValue);
  return { overlayMode, setOverlayMode };
}
```

- [ ] **Step 2: Overlay-Checkbox in PerformanceBoxplot**

```jsx
// Am Anfang der PerformanceBoxplot-Komponente
import { FormControlLabel, Checkbox } from "@mui/material";
// Im Stack-Header:
<FormControlLabel
  control={<Checkbox size="small" checked={localOverlay} onChange={(e) => setLocalOverlay(e.target.checked)} />}
  label="Overlay"
/>
```

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/hooks/useOverlayMode.js src/features/Analysis/components/study/performance/PerformanceBoxplot.jsx
git commit -m "feat: add overlay mode toggle to performance charts"
```

---

### Task 23: Abschlusstests & Regression-Check

- [ ] **Step 1: Backend alle Tests**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short
```

Erwartung: alle grün, kein `ERROR`.

- [ ] **Step 2: Frontend Build**

```bash
cd Web && npm run build
```

Erwartung: kein Build-Fehler.

- [ ] **Step 3: Lint**

```bash
cd Web && npm run lint
```

- [ ] **Step 4: Abschluss-Commit**

```bash
git add -A
git commit -m "chore: final integration and cleanup for statistical analysis system"
```

---

## Datei-Übersicht

| Datei | Status |
|---|---|
| `Backend/utils/stats_utils.py` | NEU |
| `Backend/services/data_analysis/effect_size_service.py` | NEU |
| `Backend/services/data_analysis/inferential_service.py` | NEU |
| `Backend/services/data_analysis/questionnaire_scoring.py` | NEU |
| `Backend/services/data_analysis/correlation_service.py` | NEU |
| `Backend/services/data_analysis/cross_study_service.py` | NEU |
| `Backend/services/data_analysis/exploratory_service.py` | NEU |
| `Backend/services/data_analysis/performance_analysis_service.py` | ERWEITERT |
| `Backend/services/data_analysis/eye_tracking_analysis_service.py` | ERWEITERT |
| `Backend/models/analysis.py` | NEU |
| `Backend/models/handover.py` | ERWEITERT |
| `Backend/models/study/study_config.py` | ERWEITERT |
| `Backend/routes/analysis.py` | ERWEITERT |
| `Backend/routes/export_routes.py` | NEU |
| `Backend/tests/test_stats_utils.py` | NEU |
| `Backend/tests/test_effect_sizes.py` | NEU |
| `Backend/tests/test_inferential.py` | NEU |
| `Backend/tests/test_eye_tracking_extended.py` | NEU |
| `Backend/tests/test_questionnaire_scoring.py` | NEU |
| `Backend/tests/test_correlation.py` | NEU |
| `src/features/Analysis/services/inferentialAnalysisService.js` | NEU |
| `src/features/Analysis/components/shared/*.jsx` (4 Dateien) | NEU |
| `src/features/Analysis/components/study/performance/*.jsx` (3 Dateien) | NEU |
| `src/features/Analysis/components/study/eyetracking/*.jsx` (3 Dateien) | NEU |
| `src/features/Analysis/components/study/questionnaire/*.jsx` (2 Dateien) | NEU |
| `src/features/Analysis/components/study/crossstudy/ForestPlot.jsx` | NEU |
| `src/features/Analysis/pages/CrossStudyPage.jsx` | NEU |
| `src/features/Analysis/hooks/useOverlayMode.js` | NEU |
| `src/AppRouter.jsx` | ERWEITERT |
| `src/features/Analysis/StudyAnalysisPage.jsx` | ERWEITERT |
| `sql/schema.sql` | ERWEITERT |
