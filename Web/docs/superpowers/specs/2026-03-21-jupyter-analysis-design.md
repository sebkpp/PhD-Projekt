# Design-Spec: Jupyter Analysis Environment

**Date:** 2026-03-21
**Branch:** 20-web-interface-for-data-collection
**Status:** Draft v2

---

## 1. Context & Goal

The existing web frontend under `Web/src/features/Analysis` provides fixed visualizations
for the study data. For flexible statistical analysis (t-tests, correlations, exploratory
work comparable to SPSS), a Jupyter Notebook environment is needed that accesses the
PostgreSQL database directly via the existing SQLAlchemy models.

The notebooks live at repo root level — a sibling to `Web/`, `sql/`, and `Unity/`.

---

## 2. Folder Structure

```
projekt_ws24/
├── Web/
├── sql/
├── Unity/
└── notebooks/                          ← new
    ├── utils/
    │   ├── __init__.py                 ← empty, makes utils a package
    │   └── db.py                       ← domain-specific data loader functions
    ├── 01_descriptive.ipynb            ← distributions, means, counts
    ├── 02_ttests.ipynb                 ← group comparisons (t-test, Mann-Whitney)
    └── 03_correlations.ipynb           ← cross-domain correlations
```

---

## 3. `utils/db.py` — Data Loader

### 3.1 Path Setup

The `Web/` directory is added to `sys.path` so the existing `Backend` package can be
imported. This gives access to `db_session.py`, all ORM models, and all services without
any duplication.

```python
import sys
from pathlib import Path

# Make Web/ importable from notebooks/utils/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Web"))
```

`db_session.py` uses `Path(__file__).parent / ".env"` — a path relative to its own file
location — so it finds `Web/Backend/.env` correctly regardless of where Jupyter is started.

> **Known side effect:** `db_session.py` contains a debug print statement
> (`print(f"DEBUG db_session.py: ...")`) that will appear in notebook output on first
> import. This is harmless but expected.

### 3.2 Engine Import

`engine` is already exported from `Backend/db_session.py` (line 22). No changes to
`db_session.py` are required.

```python
from Backend.db_session import engine
import pandas as pd
from sqlalchemy import text
```

### 3.3 Load Functions

Each function accepts optional `study_id` and/or `experiment_id` parameters to avoid
loading entire tables unnecessarily. Without arguments, all rows are returned.

When no filters apply, `params` is an empty dict — this is safe with `pd.read_sql`.

```python
def load_handover(study_id=None, experiment_id=None) -> pd.DataFrame:
    """Load handover records, optionally filtered by study or experiment."""
    query = "SELECT * FROM handover h JOIN trial t ON h.trial_id = t.trial_id"
    filters = []
    params = {}
    if experiment_id is not None:
        filters.append("t.experiment_id = :experiment_id")
        params["experiment_id"] = experiment_id
    if study_id is not None:
        filters.append(
            "t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    if filters:
        query += " WHERE " + " AND ".join(filters)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)  # params={} is safe when empty


def load_eyetracking(study_id=None, experiment_id=None) -> pd.DataFrame:
    """Load eye-tracking fixation records from the eye_tracking table."""
    query = (
        "SELECT et.* FROM eye_tracking et "
        "JOIN handover h ON et.handover_id = h.handover_id "
        "JOIN trial t ON h.trial_id = t.trial_id"
    )
    filters = []
    params = {}
    if experiment_id is not None:
        filters.append("t.experiment_id = :experiment_id")
        params["experiment_id"] = experiment_id
    if study_id is not None:
        filters.append(
            "t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    if filters:
        query += " WHERE " + " AND ".join(filters)
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)


def load_participants() -> pd.DataFrame:
    """Load all participant records."""
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT * FROM participant"), conn)


def load_questionnaire_responses(study_id=None) -> pd.DataFrame:
    """Load questionnaire responses joined with item metadata.
    Note: only study_id filtering is supported (no experiment_id filter).
    """
    query = (
        "SELECT qr.*, qi.questionnaire_item_text, q.questionnaire_name "
        "FROM questionnaire_response qr "
        "JOIN questionnaire_item qi ON qr.questionnaire_item_id = qi.questionnaire_item_id "
        "JOIN questionnaire q ON qi.questionnaire_id = q.questionnaire_id"
    )
    params = {}
    if study_id is not None:
        query += (
            " JOIN trial_participant_slot tps "
            "ON qr.trial_participant_slot_id = tps.trial_participant_slot_id "
            "JOIN trial t ON tps.trial_id = t.trial_id "
            "WHERE t.experiment_id IN "
            "(SELECT experiment_id FROM experiment WHERE study_id = :study_id)"
        )
        params["study_id"] = study_id
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)
```

> **Note:** `load_participants()` has no filter because the participant table is small
> and participants are not scoped to a single study.

---

## 4. Template Notebooks

Each notebook has the same skeleton structure:

```
# Section 1 — Setup & Data Loading
# Section 2 — Data Preparation (types, derived columns, missing value handling)
# Section 3 — Analysis (parametrize via variables at the top of the section)
# Section 4 — Results (tables + plots)
```

### 4.1 `01_descriptive.ipynb`

Loads all relevant tables. Shows:
- Row counts per table
- Distributions of key metrics (boxplots, histograms)
- Missing value overview

### 4.2 `02_ttests.ipynb`

Loads handover data. Section 2 builds derived columns first, then Section 3 runs the
comparison. `duration_ms` is computed from timestamp columns; `group_col` must be a
column the user adds during data preparation (e.g., from a joined stimulus condition).

```python
# --- Section 2: Data Preparation ---
df = load_handover()

# Derive duration from phase timestamps (both must be non-null)
df["duration_ms"] = (
    df["giver_released_object"] - df["giver_grasped_object"]
).dt.total_seconds() * 1000

# Join additional grouping variables here as needed
# e.g.: df = df.merge(load_participants(), on="participant_id")

# --- Section 3: Analysis — configure here ---
group_col = "is_error"      # column that defines the two groups (must exist after prep)
metric_col = "duration_ms"  # metric to compare
# -------------------------------------------

group_a = df[df[group_col] == df[group_col].unique()[0]][metric_col].dropna()
group_b = df[df[group_col] == df[group_col].unique()[1]][metric_col].dropna()

# Normality check (Shapiro-Wilk; reliable for n < 50)
# Note: checks only group_a — for rigorous analysis check both groups
_, p_norm = stats.shapiro(group_a)

# Choose parametric or non-parametric test based on normality
if p_norm > 0.05:
    stat, p = stats.ttest_ind(group_a, group_b)
    test_name = "Independent t-test"
else:
    stat, p = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")
    test_name = "Mann-Whitney U"

print(f"{test_name}: stat={stat:.3f}, p={p:.3f}")
```

### 4.3 `03_correlations.ipynb`

Loads two domains (e.g., handover + questionnaire_responses), merges on a shared key,
computes Pearson/Spearman correlations, and shows a seaborn heatmap of the correlation
matrix.

```python
import seaborn as sns

corr_matrix = merged_df[numeric_cols].corr(method="spearman")
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm")
```

---

## 5. Dependencies

`pandas`, `scipy`, `sqlalchemy`, `python-dotenv` are already in `Web/pyproject.toml`.

Add to `Web/pyproject.toml`:

```toml
[project.optional-dependencies]
notebooks = [
    "jupyterlab>=4.0",
    "ipykernel>=6.0",
    "seaborn>=0.13",
]
```

Install with:
```bash
cd Web/
uv sync --extra notebooks
```

Start Jupyter from `Web/` (where `pyproject.toml` lives), pointing to `notebooks/`:
```bash
cd Web/
uv run jupyter lab --notebook-dir=../notebooks
```

> **Why from `Web/`:** `uv run` resolves the virtualenv by walking up to the nearest
> `pyproject.toml`. Running from `notebooks/` (which has none) would fail or pick the
> wrong environment.

---

## 6. Notebook Output & Privacy

Jupyter notebooks (`.ipynb`) store cell outputs inside the file, which may include
participant data or query results. Outputs must be **cleared before committing**:

- In JupyterLab: *Edit → Clear All Outputs* before saving/committing.
- Alternatively, `nbstripout` can be added as a pre-commit hook to strip outputs
  automatically (optional, not in this spec).

A `.gitignore` in `notebooks/` should exclude Jupyter artefacts but not the notebooks themselves:

```
# notebooks/.gitignore
.ipynb_checkpoints/
utils/__pycache__/
```

---

## 7. Files Overview

| File | Action |
|---|---|
| `notebooks/utils/__init__.py` | New — empty package marker |
| `notebooks/utils/db.py` | New — load functions per domain |
| `notebooks/01_descriptive.ipynb` | New — descriptive statistics template |
| `notebooks/02_ttests.ipynb` | New — t-test / Mann-Whitney template |
| `notebooks/03_correlations.ipynb` | New — correlation analysis template |
| `Web/pyproject.toml` | Modify — add `[project.optional-dependencies] notebooks` |

`Web/Backend/db_session.py` — **no changes needed.**

---

## 8. Out of Scope

- Authentication for DB access (notebooks run locally, same machine as DB)
- Automated report generation / PDF export
- Integration with the web frontend
- `nbstripout` pre-commit hook setup
