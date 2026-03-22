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

**Why not mocks?** The orchestrating functions use nested ORM relationships (e.g., `et.aoi.aoi`, `handover.eye_trackings`). Mocking these accurately is more complex than using a real DB, and mocks cannot catch SQL query bugs.

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
    session.close()
```

Allows tests to call service functions directly: `analyze_experiment_eye_tracking(db_session, experiment_id)`.

### Test Data Pattern

Each integration test builds a minimal data chain via a mix of:
- **API fixtures** (existing): `study_id`, `experiment_id`, `trial_id`, `handover_id`
- **Direct ORM inserts** (via `SessionLocal`): `EyeTracking`, `AreaOfInterest`, `QuestionnaireResponse`, `QuestionnaireItem`, `Questionnaire` — for fine-grained data that has no API endpoint or requires specific field values (e.g., `starttime`, `duration`, `aoi_id`)

Minimal data chain:
```
Study → Experiment → Trial → Handover → EyeTracking (with starttime, duration, aoi)
                           → QuestionnaireResponse (with participant, item, value)
```

---

## Functions to Test

### `eye_tracking_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `_assign_phase(et_starttime, handover)` | Unit | Pure function, no DB |
| `_build_aoi_label_map(session)` | Integration | Needs `AreaOfInterest` rows |
| `_compute_aoi_stats(eye_trackings, aoi_label_map, total_ms)` | Unit | Uses ORM-like objects, testable with simple mocks |
| `analyze_experiment_eye_tracking(session, id)` | Integration | Main per-experiment aggregation |
| `analyze_study_eye_tracking(session, id)` | Integration | Cross-experiment aggregation by condition |
| `analyze_experiment_eye_tracking_phases(session, id)` | Integration | Phase 1/2/3 AOI breakdown |
| `analyze_experiment_eye_tracking_transitions(session, id)` | Integration | AOI transition matrix |
| `analyze_experiment_ppi(session, id)` | Integration | Proactive Planning Index |
| `analyze_experiment_saccade_rate(session, id)` | Integration | Saccade rate giver/receiver |

### `questionnaire_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `build_response_dataframe(responses)` | Unit | Uses ORM-like mock objects |
| `compute_trial_item_stats(df, stimuli_map, ...)` | Unit | Pure pandas logic |
| `compute_mean_diffs(stats)` | Unit | Pure dict logic |
| `build_participant_result(responses)` | Unit | Uses ORM-like mock objects |
| `analyze_experiment_questionnaires(session, id)` | Integration | Full experiment analysis |
| `analyze_study_questionnaires(session, id)` | Integration | Cross-experiment inferential |

### `performance_analysis_service.py`

| Function | Test Type | Notes |
|---|---|---|
| `calc_stats(data)` | Unit | Pure pandas/scipy |
| `analyze_experiment_performance(session, id)` | Integration | Per-experiment handover stats |

---

## Files Changed

| File | Change |
|---|---|
| `Backend/tests/conftest.py` | Add `db_session` fixture |
| `Backend/tests/test_eye_tracking_analysis.py` | Extend with integration tests |
| `Backend/tests/test_questionnaire_analysis.py` | Extend with integration tests |
| `Backend/tests/test_performance_analysis.py` | Add `calc_stats` + `analyze_experiment_performance` |

No new test files are created — related tests stay together in existing files.

---

## Test Design Principles

- Each test uses the minimal data set needed to exercise the target code path
- Edge cases covered per function: empty study/experiment, missing timestamps, no data for a condition
- Integration tests assert on response structure (keys present) and basic value correctness (non-negative, within expected range)
- `clean_db` ensures test isolation — no test depends on another's data
