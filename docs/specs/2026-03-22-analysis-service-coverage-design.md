# Design: Backend Test Coverage Improvement

**Date:** 2026-03-22
**Goal:** Raise overall backend test coverage from 65.83% to >80%.

---

## Context

Coverage analysis revealed gaps in three layers:

| Layer | Problem |
|---|---|
| **Analysis services** | Core research logic almost completely untested (28–64%) |
| **Feature paths** | Study-with-stimuli/questionnaires service path never exercised |
| **Routes** | Analysis endpoints only hit 404 (empty DB); two export endpoints have no tests |

Additionally, several files were identified as dead code to be deleted rather than tested.

### Coverage Targets

| File | Current | Target |
|---|---|---|
| `eye_tracking_analysis_service.py` | 28% | ~85% |
| `questionnaire_analysis_service.py` | 38% | ~85% |
| `performance_analysis_service.py` | 64% | ~85% |
| `experiment_service.py` | 62% | ~75% |
| `study_service.py` | 62% | ~80% |
| `questionnaire_response_service.py` | 57% | ~80% |
| `routes/analysis.py` | 68% | ~80% |
| **Overall** | **65.83%** | **>80%** |

---

## Dead Code — Delete, Don't Test

The following code is unreachable from any active HTTP route and should be deleted rather than tested. Deleting dead code removes noise from the coverage report and eliminates confusion for future developers.

### `Backend/db/trial_repository.py`
All function definitions are commented out (lines 5–45). The file has three live import lines at the top but no callable functions. No other module imports from this file (verified via grep). Safe to delete.

### `Backend/services/participant_submission_service.py`
Manages in-memory state that was superseded by the DB-backed approach in `participant_service.py`. The call into this service is commented out (line 37 of `participant_service.py`). **However, the import on line 8 of `participant_service.py` is still active:**
```python
from .participant_submission_service import (
    submit_participant_to_slot as internal_submit,
)
```
Both the module deletion and this import removal must happen together, otherwise `participant_service.py` will fail to import at startup.

### `trialConfig` block in `Backend/services/experiment_service.py` (lines 24–37)
The `POST /experiments/` route uses a Pydantic model (`ExperimentCreateRequest`) that only declares `name`, `study_id`, `description`, `researcher`. Pydantic silently strips any additional fields before calling `create_experiment`, so `settings.get("trialConfig", {})` always returns `{}`. The `trial_config` variable assignment on line 24 and the entire `if trial_config:` block (lines 25–37) are unreachable through any active HTTP route.

Both the variable assignment (line 24) and the `if trial_config:` block (lines 25–37) should be deleted, along with the now-unused imports of `TrialRepository` (line 8), `TrialSlotRepository` (line 9), and `TrialSlotStimulusRepository` (line 10). This also explains why `db/trial/trial_slot_repository.py` (46%) and `db/trial/trial_slot_stimulus.py` (32%) have low coverage — their `create` methods are only called from this dead block.

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
    session.rollback()
    session.close()
```

`session.rollback()` in teardown handles the **failure path**: if a test raises mid-execution before a `commit()`, the rollback discards partial writes so the `clean_db` sweep (which runs in a separate session) finds a consistent state.

On the **success path**, test setup calls `session.commit()` to persist data, the service function runs, and the teardown `rollback()` is a no-op — actual cleanup is performed by `clean_db` which issues DELETEs in its own session after the test function returns.

### Test Data Pattern

Each integration test builds a minimal data chain via a mix of:
- **API fixtures** (existing): `study_id`, `experiment_id`, `participant_id`
- **Direct ORM inserts** (via `db_session`): `Trial`, `Handover`, `EyeTracking`, `AreaOfInterest`, `QuestionnaireResponse`, `QuestionnaireItem`, `Questionnaire` — for fine-grained data that has no API endpoint or requires specific field values. Add `trial_id` and `handover_id` fixtures to `conftest.py` via API calls.

Minimal data chain:
```
Study → Experiment → Trial → Handover → EyeTracking (with starttime, duration, aoi)
                           → QuestionnaireResponse (with participant, item, value)
```

**Commit semantics:** `db_session.py` configures `autoflush=False`. All direct ORM inserts in test setup **must call `db_session.commit()`** — not `db_session.flush()` — before invoking the service function. The service functions open their own `SessionLocal()` instances (separate sessions), and rows committed to one session are only visible to another session after a `commit()`. Using `flush()` makes rows visible within the same session but not across session boundaries, which will silently produce empty query results from the service.

---

## Work Groups

### Group 1 — Analysis Services (Primary)

The three core research services. All orchestrating functions are untested. These have the highest impact on both coverage and research validity.

#### `eye_tracking_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `_assign_phase(et_starttime, handover)` | Unit | Pure. Cases: each of phases 1/2/3, outside all phases, `et_starttime=None`, all handover timestamps `None` |
| `_build_aoi_label_map(session)` | Integration | Happy path + empty table |
| `_compute_aoi_stats(eye_trackings, aoi_label_map, total_ms)` | Unit | `et.aoi` set to object with `.aoi` attr OR `None` (tests `str(et.aoi_id)` fallback); cover `total_duration_ms=0` |
| `analyze_experiment_eye_tracking(session, id)` | Integration | Happy path; empty experiment |
| `analyze_study_eye_tracking(session, id)` | Integration | Happy path with 2 conditions; empty study |
| `analyze_experiment_eye_tracking_phases(session, id)` | Integration | Happy path; all handover timestamps `None` → empty phase dicts (not exception) |
| `analyze_experiment_eye_tracking_transitions(session, id)` | Integration | Happy path; `et.starttime=None` → sort uses `datetime.min` without raising |
| `analyze_experiment_ppi(session, id)` | Integration | Happy path (giver+receiver in phase 3); no phase-3 records → `ppi_giver=None` |
| `analyze_experiment_saccade_rate(session, id)` | Integration | Happy path; empty experiment |

#### `questionnaire_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `build_response_dataframe(responses)` | Unit | ORM-like mocks with `r.participant_id`, `r.trial_id`, `r.questionnaire_item_id`, `r.response_value`, `r.questionnaire_item.questionnaire.questionnaire_id/name`, `r.questionnaire_item.item_name`; empty list → empty DataFrame |
| `compute_trial_item_stats(df, stimuli_map, ...)` | Unit | Normal case; single-item questionnaire; `trial_number_map=None` |
| `compute_mean_diffs(stats)` | Unit | Two trials → diffs computed; single trial → `{}` (not missing key) |
| `build_participant_result(responses)` | Unit | ORM-like mocks; empty list |
| `analyze_experiment_questionnaires(session, id)` | Integration | Happy path; trials with zero responses (see known bug below) |
| `analyze_study_questionnaires(session, id)` | Integration | Happy path with 2 conditions and sufficient n; empty study |

#### `performance_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `calc_stats(data)` | Unit | Normal list (n≥4 for Shapiro-Wilk); n=1 (std/CI/skew return None/NaN paths) |
| `analyze_experiment_performance(session, id)` | Integration | Happy path; empty experiment |
| `analyze_study_performance(session, id)` | Integration (smoke) | Empty study → `{}`; existing mock tests cover inferential path |

---

### Group 2 — Study with Stimuli and Questionnaires

`study_service.create_study` and `study_service.update_study` contain branches for processing `stimuli` and `questionnaires` sub-objects. Note: `StudyCreate` and `StudyUpdate` Pydantic models do **not** declare these fields, so they cannot be exercised through the HTTP API. Tests must call the service functions directly using `db_session`.

**Files covered:**

| File | Current | What's uncovered |
|---|---|---|
| `services/study_service.py` | 62% | `create_study` stimuli/questionnaire loops; `update_study` stimuli/questionnaire branches |
| `db/study/study_questionnaire_repository.py` | 34% | `create`, `delete_all_by_study_id` |
| `db/study/study_config_repository.py` | 52% | `update_study_config` |
| `db/study/study_repository.py` | 48% | `update` branches for stimuli/questionnaire list changes |

**Tests:** `test_study.py` — add direct service-level tests:
1. Call `study_service.create_study(db_session, {..., "stimuli": [...], "questionnaires": [...]})` → verify records in `study_questionnaire` table
2. Call `study_service.update_study(db_session, study_id, {"questionnaires": [...], "stimuli": [...]})` → verify `delete_all` + re-create

---

### Group 3 — Questionnaire Response Service Data Paths

The happy-path entry points are covered, but all tests run against an empty DB, so the data-building loop bodies never execute.

**File:** `services/questionnaire_response_service.py` (57%)

**Uncovered paths:**
- `get_questionnaire_responses_for_experiment` data-building loop — `responses` is always empty in current tests
- `are_all_questionnaires_in_trial_done` return `True` path — requires actual responses matching all questionnaire items
- `are_all_questionnaires_done` full loop body

**Tests:** `test_questionnaire.py` — add tests that seed questionnaire items and responses, then verify `get_questionnaire_responses_for_experiment` returns structured data, and `are_all_questionnaires_done` returns `True` when all items are answered.

---

### Group 4 — Analysis Route 200 Paths and Missing Endpoints

All DB-backed analysis endpoints currently only hit the 404 branch because no test seeds handover/eye-tracking data. Additionally, two endpoints have no tests at all.

**File:** `routes/analysis.py` (68%)

**Uncovered paths:**
- Every DB-backed endpoint's 200 response path (always 404 due to empty DB)
- `GET /study/{id}/eye-tracking` (hyphenated alias) — only the `/eyetracking` form is tested
- `GET /study/{id}/export/csv` — no test
- `GET /study/{id}/export/xlsx` — no test

**Tests:** `test_analysis_routes.py` — add:
1. Seed minimal handover + eye-tracking + questionnaire-response data via fixtures, then call each DB-backed endpoint and assert 200 with expected top-level keys
2. Test the hyphenated alias endpoint returns 200
3. Test CSV and XLSX export endpoints return correct `Content-Type` and non-empty body

---

### Group 5 — Minor Route Gap

| File | Gap | Fix |
|---|---|---|
| `routes/questionnaire.py` (79%) | `GET /questionnaires/{id}` only tested for 404; 200 path missing | Add one test that creates a questionnaire and fetches it by ID |

Routes' `except/rollback` branches are excluded — testing DB failure scenarios requires SQLAlchemy-level exception injection with low return on investment.

---

## Known Service Bug: `analyze_experiment_questionnaires` with No Responses

When `responses` is empty, `build_response_dataframe([])` returns a DataFrame with no columns. `compute_trial_item_stats` then calls `df.groupby(["trial_id", ...])` which raises `KeyError` on missing columns.

Fix — add guard in `analyze_experiment_questionnaires` before `compute_trial_item_stats`:
```python
df = build_response_dataframe(responses)
if df.empty:
    return {"experiment_id": experiment_id, "participants": {}, "trial_item_stats": {}, "mean_diffs": {}}
```

Note: `build_participant_result(responses)` on an empty list returns `{}` without error — no second guard is needed.

This fix must be applied alongside the integration test that covers this path.

---

## Files Changed

| File | Change |
|---|---|
| `Backend/db/trial_repository.py` | **Delete** (dead code) |
| `Backend/services/participant_submission_service.py` | **Delete** (dead code) |
| `Backend/services/participant_service.py` | Remove dead import of `participant_submission_service` (line 8) |
| `Backend/services/experiment_service.py` | Delete `trial_config` assignment (line 24) + `if trial_config:` block (lines 25–37); remove unused imports `TrialRepository` (line 8), `TrialSlotRepository` (line 9), `TrialSlotStimulusRepository` (line 10) |
| `Backend/tests/conftest.py` | Add `db_session` fixture; add `trial_id` and `handover_id` API-based fixtures |
| `Backend/tests/test_eye_tracking_analysis.py` | Add unit tests (`_assign_phase`, `_compute_aoi_stats`) + integration tests |
| `Backend/tests/test_questionnaire_analysis.py` | Add unit tests (pandas helpers) + integration tests |
| `Backend/tests/test_performance_analysis.py` | Add `calc_stats` unit tests + integration tests |
| `Backend/tests/test_study.py` | Add direct service-level tests for stimuli/questionnaire paths (Group 2) |
| `Backend/tests/test_questionnaire.py` | Add seeded-data response tests + `get_by_id` 200 test (Groups 3 + 5) |
| `Backend/tests/test_analysis_routes.py` | Add seeded-data 200-path tests + alias + export tests (Group 4) |
| `Backend/services/data_analysis/questionnaire_analysis_service.py` | Fix empty-responses crash |

---

## Test Design Principles

- Each test uses the minimal data set needed to exercise the target code path
- All direct ORM inserts in test setup call `session.commit()` — never `session.flush()` — before the service function is invoked. `flush()` is insufficient because service functions open separate `SessionLocal()` instances and only see committed rows
- Integration tests assert on response structure (keys present) and basic value correctness
- `clean_db` (autouse) + `db_session` rollback ensure full test isolation
- Exception/rollback branches in routes are excluded — testing DB failures requires SQLAlchemy-level injection with low ROI
- Utility repository methods with no callers (`add`, `delete`, `get_all`) are excluded — testing unreachable code provides no value
