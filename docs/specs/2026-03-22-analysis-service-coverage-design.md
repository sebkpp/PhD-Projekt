# Design: Analysis Service Test Coverage

**Date:** 2026-03-22
**Goal:** Raise overall backend test coverage from 65.83% to >80%, with focus on the three critical analysis services.

---

## Context

The backend has three analysis services with critically low coverage:

| Service | Current | Target |
|---|---|---|
| `eye_tracking_analysis_service.py` | 28% | ~85% |
| `questionnaire_analysis_service.py` | 38% | ~85% |
| `performance_analysis_service.py` | 64% | ~85% |
| **Overall** | **65.83%** | **>80%** |

Each service has a split structure:
- **Pure/utility functions** — already tested via unit tests
- **DB-orchestrating functions** — almost completely untested; these take a SQLAlchemy `session`, query repositories and ORM models, and perform the core research analysis

---

## Approach: Integration Tests with Real Test Database

Use the existing CI test database infrastructure. The `conftest.py` already provides:
- `clean_db` (autouse) — wipes all tables before/after each test
- `client` — FastAPI TestClient
- `study_id`, `experiment_id`, `participant_id` — API-based fixtures

The CI workflow (`workflow.yml`) sets up a real PostgreSQL `testdb` and runs `sql/schema.sql` before each test run, so integration tests work identically locally and in CI without any workflow changes.

**Why not mocks?** The orchestrating functions use nested ORM relationships (e.g., `et.aoi.aoi`, `handover.eye_trackings`, `r.questionnaire_item.questionnaire.name`). Mocking these accurately is more complex than using a real DB, and mocks cannot catch SQL query bugs.

---

## Architecture

### New Fixture: `db_session`

Added to `Backend/tests/conftest.py`:

```python
@pytest.fixture
def db_session():
    from Backend.db_session import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()   # ensure no partial transaction bleeds into clean_db teardown
    session.close()
```

`session.rollback()` in teardown prevents a partially-committed or aborted transaction from interfering with the `clean_db` fixture's DELETE sweep, which runs in a separate session.

Allows tests to call service functions directly: `analyze_experiment_eye_tracking(db_session, experiment_id)`.

### Test Data Pattern

Each integration test builds a minimal data chain via a mix of:
- **API fixtures** (existing): `study_id`, `experiment_id`, `trial_id`, `handover_id`
- **Direct ORM inserts** (via `db_session` fixture): `EyeTracking`, `AreaOfInterest`, `QuestionnaireResponse`, `QuestionnaireItem`, `Questionnaire` — for fine-grained data that has no API endpoint or requires specific field values (e.g., `starttime`, `duration`, `aoi_id`)

Minimal data chain:
```
Study → Experiment → Trial → Handover → EyeTracking (with starttime, duration, aoi)
                           → QuestionnaireResponse (with participant, item, value)
```

**Commit semantics:** `db_session.py` configures `autoflush=False`. All direct ORM inserts in test setup **must call `db_session.commit()`** before invoking the service function. The service functions open repository instances on the same session, and repository queries will not see uncommitted rows without an explicit commit or flush.

---

## Functions to Test

### `eye_tracking_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `_assign_phase(et_starttime, handover)` | Unit | Pure function. Cases: each of phases 1/2/3, outside all phases, `et_starttime=None`, all handover timestamps `None` |
| `_build_aoi_label_map(session)` | Integration | Happy path + empty table |
| `_compute_aoi_stats(eye_trackings, aoi_label_map, total_ms)` | Unit | Mock objects need `et.aoi` set to object with `.aoi` attr OR `None` (tests the `str(et.aoi_id)` fallback), and `et.duration`. Cover: `total_duration_ms=0` (percentage=0 path) |
| `analyze_experiment_eye_tracking(session, id)` | Integration | Happy path; empty experiment (no trials) |
| `analyze_study_eye_tracking(session, id)` | Integration | Happy path with 2 conditions; empty study |
| `analyze_experiment_eye_tracking_phases(session, id)` | Integration | Happy path; all handover timestamps `None` → empty phase dicts (not exception) |
| `analyze_experiment_eye_tracking_transitions(session, id)` | Integration | Happy path; `et.starttime=None` on some records → sort falls back to `datetime.min` without raising |
| `analyze_experiment_ppi(session, id)` | Integration | Happy path (giver+receiver records in phase 3); no phase-3 records → `ppi_giver=None, ppi_receiver=None` |
| `analyze_experiment_saccade_rate(session, id)` | Integration | Happy path; empty experiment |

### `questionnaire_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `build_response_dataframe(responses)` | Unit | ORM-like mocks: set `r.participant_id`, `r.trial_id`, `r.questionnaire_item_id`, `r.response_value`, `r.questionnaire_item.questionnaire.questionnaire_id`, `r.questionnaire_item.questionnaire.name`, `r.questionnaire_item.item_name`. Also test empty list → empty DataFrame |
| `compute_trial_item_stats(df, stimuli_map, ...)` | Unit | Normal case; single-item questionnaire; missing `trial_number_map` (None) |
| `compute_mean_diffs(stats)` | Unit | Two trials → diffs computed; single trial → `mean_diffs={}` (not missing key) |
| `build_participant_result(responses)` | Unit | ORM-like mocks (same fields as `build_response_dataframe`); empty list |
| `analyze_experiment_questionnaires(session, id)` | Integration | Happy path; **experiment with trials but zero responses** — this will surface a latent `KeyError` crash in `compute_trial_item_stats` when the DataFrame is empty (no columns). The implementor must simultaneously fix the service: guard with `if df.empty: return {}` before the groupby |
| `analyze_study_questionnaires(session, id)` | Integration | Happy path with 2 conditions and sufficient n; empty study |

### `performance_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `calc_stats(data)` | Unit | Normal list (n≥4 for Shapiro-Wilk); n=1 (std/CI/skew return None/NaN paths) |
| `analyze_experiment_performance(session, id)` | Integration | Happy path; empty experiment (no handovers) |
| `analyze_study_performance(session, id)` | Integration (supplement) | The existing mock-based tests cover this function. Add one integration smoke test (empty study → `{}`) to verify the DB query path works end-to-end |

---

## Known Service Bug: `analyze_experiment_questionnaires` with No Responses

When `responses` is empty, `build_response_dataframe([])` returns a DataFrame with no columns. `compute_trial_item_stats` then calls `df.groupby(["trial_id", ...])` which raises `KeyError` on missing columns.

The fix is a guard in `analyze_experiment_questionnaires`:
```python
df = build_response_dataframe(responses)
if df.empty:
    return {"experiment_id": experiment_id, "participants": {}, "trial_item_stats": {}, "mean_diffs": {}}
```

This fix must be applied alongside the integration test that covers this path.

---

## Files Changed

| File | Change |
|---|---|
| `Backend/tests/conftest.py` | Add `db_session` fixture with rollback teardown |
| `Backend/tests/test_eye_tracking_analysis.py` | Extend with unit tests for `_assign_phase`, `_compute_aoi_stats` and integration tests |
| `Backend/tests/test_questionnaire_analysis.py` | Extend with unit tests for pandas helpers and integration tests |
| `Backend/tests/test_performance_analysis.py` | Add `calc_stats` unit tests, `analyze_experiment_performance` integration test, `analyze_study_performance` smoke test |
| `Backend/services/data_analysis/questionnaire_analysis_service.py` | Fix empty-responses crash in `analyze_experiment_questionnaires` |

No new test files are created — related tests stay together in existing files.

---

## Test Design Principles

- Each test uses the minimal data set needed to exercise the target code path
- All direct ORM inserts in test setup call `session.commit()` before the service function is invoked
- Integration tests assert on response structure (keys present) and basic value correctness (non-negative, within expected range)
- `clean_db` (autouse) + `db_session` rollback ensure full test isolation — no test depends on another's data
