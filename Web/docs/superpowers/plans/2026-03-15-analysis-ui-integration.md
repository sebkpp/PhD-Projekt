# Analysis UI Integration — Session A Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all three Analysis pages fully functional, implement lazy tab loading, add 3 new backend endpoints, migrate questionnaire service to N-condition inferential tests, and delete orphaned components.

**Architecture:** Lazy tab loading via `loadedTabs` Set + `enabled` hook flag. CSS-visibility tab panels preserve hook state. Backend adds phase/transition/PPI endpoints reusing existing service utilities. ExperimentAnalysisPage is purely descriptive; StudyAnalysisPage shows inferential results.

**Tech Stack:** FastAPI (Python), React + Vite, Recharts, Plotly, Ant Design, Tailwind CSS, pingouin (statistics)

**Spec:** `docs/superpowers/specs/2026-03-15-analysis-ui-integration-design.md`

---

## Chunk 1: Backend

### Task 1: Questionnaire Service — Migrate to N-Condition Inferential Tests

**Files:**
- Modify: `Backend/services/data_analysis/questionnaire_analysis_service.py:396–408`
- Test: `Backend/tests/test_analysis.py`

**Context:** `analyze_study_questionnaires` currently calls `run_paired_test(vals_a, vals_b)` (k=2 only). Replace with `run_inferential_analysis(cond_dict)` which supports N conditions.

- [ ] **Step 1: Write a smoke test for the new questionnaire endpoint**

Add to `Backend/tests/test_analysis.py`:

```python
def test_analysis_questionnaires_study_returns_valid_structure(client, study_id):
    """Study questionnaire response must contain study_id and questionnaires keys."""
    resp = client.get(f"/analysis/study/{study_id}/questionnaires")
    assert resp.status_code < 500
    if resp.status_code == 200:
        data = resp.json()
        assert "study_id" in data
        assert "questionnaires" in data
```

Run: `uv run pytest Backend/tests/test_analysis.py::test_analysis_questionnaires_study_returns_valid_structure -v`
Expected: PASS (structure already correct, test validates nothing breaks after migration)

- [ ] **Step 2: Migrate `analyze_study_questionnaires` in questionnaire_analysis_service.py**

In `Backend/services/data_analysis/questionnaire_analysis_service.py`:

Replace the import at line 5:
```python
# OLD:
from Backend.utils.stats_utils import run_paired_test
# NEW — add alongside existing imports:
from Backend.services.data_analysis.inferential_service import run_inferential_analysis
```

Replace lines 394–408 **in full** (the entire inferential block from the comment down to the closing `inferential[item_name] = None`, including the `inferential: dict = {}` declaration and the `if len(conditions) >= 2:` outer guard — both are preserved in the replacement):
```python
        # Build inferential tests (N conditions per item using run_inferential_analysis)
        inferential: dict[str, dict | None] = {}
        if len(conditions) >= 2:
            for item_name in sorted(item_names):
                cond_dict = {
                    cond: condition_item_values[cond].get(item_name, [])
                    for cond in conditions
                    if condition_item_values[cond].get(item_name)
                }
                if len(cond_dict) >= 2 and all(len(v) >= 3 for v in cond_dict.values()):
                    inferential[item_name] = run_inferential_analysis(cond_dict)
                else:
                    inferential[item_name] = None
```

Also remove the now-unused `run_paired_test` import line.

- [ ] **Step 3: Run test to verify it still passes**

Run: `uv run pytest Backend/tests/test_analysis.py -v`
Expected: All PASS (no 500 errors)

- [ ] **Step 4: Commit**

```bash
git add Backend/services/data_analysis/questionnaire_analysis_service.py Backend/tests/test_analysis.py
git commit -m "feat: migrate questionnaire analysis to N-condition inferential tests"
```

---

### Task 2: New Backend Endpoints — ET Phases, Transitions, PPI

**Files:**
- Modify: `Backend/services/data_analysis/eye_tracking_analysis_service.py` (add 3 functions)
- Modify: `Backend/routes/analysis.py` (add 3 route handlers)
- Test: `Backend/tests/test_analysis.py`

**Context:** `EyeTracking` ORM model has `starttime`, `endtime`, `duration`, `aoi_id`, `participant_id`. `Handover` has phase timestamps: `giver_grasped_object` (Phase 1 start), `receiver_touched_object` (Phase 1→2), `receiver_grasped_object` (Phase 2→3), `giver_released_object` (Phase 3 end). Phases are assigned by comparing ET `starttime` to handover timestamp boundaries.

- [ ] **Step 1: Write failing route tests**

Add to `Backend/tests/test_analysis.py`:

```python
def test_analysis_eyetracking_phases_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/phases")
    assert resp.status_code < 500

def test_analysis_eyetracking_transitions_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/transitions")
    assert resp.status_code < 500

def test_analysis_ppi_experiment(client, experiment_id):
    resp = client.get(f"/analysis/experiment/{experiment_id}/ppi")
    assert resp.status_code < 500
```

Run: `uv run pytest Backend/tests/test_analysis.py::test_analysis_eyetracking_phases_experiment -v`
Expected: FAIL with 404 (route doesn't exist yet)

- [ ] **Step 2: Add 4 new functions to `eye_tracking_analysis_service.py`** (all written from scratch — none of these exist yet)

**Note on null-safety:** `_assign_phase` uses `if t1 and t2 and ...` — Python short-circuits on `None`, so `None and datetime` evaluates to `False` without comparison. No `TypeError` risk even if handover timestamps are `None`.

Append to the end of `Backend/services/data_analysis/eye_tracking_analysis_service.py`:

```python
def _assign_phase(et_starttime, handover) -> int | None:
    """
    Determine which handover phase (1, 2, 3) an eye-tracking record belongs to,
    based on the ET starttime relative to handover phase-boundary timestamps.

    Phase 1 (Coordination): giver_grasped_object → receiver_touched_object
    Phase 2 (Grasp):        receiver_touched_object → receiver_grasped_object
    Phase 3 (Transfer):     receiver_grasped_object → giver_released_object
    Returns None if timestamps are missing or ET is outside all phases.
    """
    if et_starttime is None:
        return None
    t1 = handover.giver_grasped_object
    t2 = handover.receiver_touched_object
    t3 = handover.receiver_grasped_object
    t4 = handover.giver_released_object
    if t1 and t2 and t1 <= et_starttime < t2:
        return 1
    if t2 and t3 and t2 <= et_starttime < t3:
        return 2
    if t3 and t4 and t3 <= et_starttime <= t4:
        return 3
    return None


def analyze_experiment_eye_tracking_phases(session, experiment_id: int) -> dict:
    """
    Per-trial, per-phase AOI dwell-time breakdown.
    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "phases": {
            1: { aoi_name: {"label": str, "total_duration_ms": int, "percentage": float} },
            2: { ... },
            3: { ... }
          }
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)
    aoi_label_map = _build_aoi_label_map(session)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)
        # phase → aoi_name → list of durations
        phase_aoi_durations: dict[int, dict[str, list]] = {1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list)}
        phase_total_ms: dict[int, int] = {1: 0, 2: 0, 3: 0}

        for handover in handovers:
            for et in handover.eye_trackings:
                phase = _assign_phase(et.starttime, handover)
                if phase is None:
                    continue
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                dur = et.duration if et.duration is not None else 0
                phase_aoi_durations[phase][aoi_name].append(dur)
                phase_total_ms[phase] += dur

        phases_result = {}
        for phase_num in (1, 2, 3):
            total_ms = phase_total_ms[phase_num]
            phase_result = {}
            for aoi_name, durations in phase_aoi_durations[phase_num].items():
                total_dur = sum(durations)
                pct = (total_dur / total_ms * 100.0) if total_ms > 0 else 0.0
                phase_result[aoi_name] = {
                    "label": aoi_label_map.get(aoi_name, aoi_name),
                    "total_duration_ms": total_dur,
                    "percentage": round(pct, 4),
                }
            phases_result[phase_num] = phase_result

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "phases": phases_result,
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}


def analyze_experiment_eye_tracking_transitions(session, experiment_id: int) -> dict:
    """
    Per-trial AOI transition matrix (AOI sequence ordered by starttime).
    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "transitions": { "aoi_from->aoi_to": count, ... },
          "aoi_sequence": [aoi_name, ...]
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)
    aoi_label_map = _build_aoi_label_map(session)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)
        all_et = []
        for handover in handovers:
            for et in handover.eye_trackings:
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                all_et.append((et.starttime, aoi_name))

        # Sort by starttime, build sequence
        all_et.sort(key=lambda x: x[0] if x[0] is not None else "")
        aoi_sequence = [aoi for _, aoi in all_et]
        transitions = calc_transitions(aoi_sequence)

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "transitions": transitions,
            "aoi_sequence_length": len(aoi_sequence),
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}


def analyze_experiment_ppi(session, experiment_id: int) -> dict:
    """
    Proactive Planning Index per trial, split by participant role (giver/receiver).

    PPI = dwell_time("environment", phase=3) / total_phase3_duration * 100

    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "ppi_giver": float | None,
          "ppi_receiver": float | None
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)

        # Collect phase-3 ET records per role
        giver_records = []
        receiver_records = []

        for handover in handovers:
            for et in handover.eye_trackings:
                phase = _assign_phase(et.starttime, handover)
                if phase != 3:
                    continue
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                dur = et.duration if et.duration is not None else 0
                # Phase 3 duration: giver_released_object - receiver_grasped_object in ms
                t3 = handover.receiver_grasped_object
                t4 = handover.giver_released_object
                if t3 and t4:
                    phase3_dur_ms = int((t4 - t3).total_seconds() * 1000)
                else:
                    phase3_dur_ms = 0
                record = {
                    "aoi_name": aoi_name,
                    "phase": 3,
                    "dwell_time_ms": dur,
                    "duration_ms": phase3_dur_ms,
                }
                if et.participant_id == handover.giver:
                    giver_records.append(record)
                else:
                    receiver_records.append(record)

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "ppi_giver": calc_ppi(giver_records) if giver_records else None,
            "ppi_receiver": calc_ppi(receiver_records) if receiver_records else None,
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}
```

- [ ] **Step 3: Add 3 route handlers to `Backend/routes/analysis.py`**

Add after the existing `experiment_eyetracking_analysis` handler (after line 185):

```python
from Backend.services.data_analysis.eye_tracking_analysis_service import (
    analyze_experiment_eye_tracking,
    analyze_study_eye_tracking,
    analyze_experiment_eye_tracking_phases,
    analyze_experiment_eye_tracking_transitions,
    analyze_experiment_ppi,
)
```

Update the existing import block at the top of `analysis.py` — replace the eye tracking import line with the extended version above.

Then add the three new route handlers after the existing `experiment_eyetracking_analysis` function:

```python
@router.get(
    "/experiment/{experiment_id}/eyetracking/phases",
    status_code=status.HTTP_200_OK,
    summary="Eye-tracking phase breakdown for an experiment",
    description="Return per-trial AOI dwell-time grouped by handover phase (1=Coordination, 2=Grasp, 3=Transfer).",
)
async def experiment_eyetracking_phases(experiment_id: int, db=Depends(get_db)):
    try:
        result = analyze_experiment_eye_tracking_phases(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No eye-tracking data found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiment/{experiment_id}/eyetracking/transitions",
    status_code=status.HTTP_200_OK,
    summary="AOI transition matrix for an experiment",
    description="Return per-trial AOI transition counts (ordered by fixation starttime).",
)
async def experiment_eyetracking_transitions(experiment_id: int, db=Depends(get_db)):
    try:
        result = analyze_experiment_eye_tracking_transitions(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No eye-tracking data found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiment/{experiment_id}/ppi",
    status_code=status.HTTP_200_OK,
    summary="Proactive Planning Index for an experiment",
    description="PPI = environment dwell-time in phase 3 / total phase-3 duration × 100, split by giver/receiver.",
)
async def experiment_ppi(experiment_id: int, db=Depends(get_db)):
    try:
        result = analyze_experiment_ppi(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No handover data found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
```

- [ ] **Step 4: Run all new tests**

Run: `uv run pytest Backend/tests/test_analysis.py -v`
Expected: All PASS (new routes return 200 or 404, not 500)

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest Backend/tests/ -v`
Expected: All PASS (no regressions)

- [ ] **Step 6: Commit**

```bash
git add Backend/services/data_analysis/eye_tracking_analysis_service.py Backend/routes/analysis.py Backend/tests/test_analysis.py
git commit -m "feat: add eyetracking/phases, eyetracking/transitions, and ppi experiment endpoints"
```

---

## Chunk 2: Frontend Infrastructure

### Task 3: Add `enabled` Flag to All 6 Existing Hooks

**Files:**
- Modify: `src/features/Analysis/hooks/useStudyPerformanceMetrics.js`
- Modify: `src/features/Analysis/hooks/useStudyUxMetrics.js`
- Modify: `src/features/Analysis/hooks/useStudyEyeTrackingMetrics.js`
- Modify: `src/features/Analysis/hooks/usePerformanceMetrics.js`
- Modify: `src/features/Analysis/hooks/useUxMetrics.js`
- Modify: `src/features/Analysis/hooks/useEyeTrackingMetrics.js`

**Pattern for all 6 hooks** — same change in each:
1. Add `enabled = true` as second parameter
2. Change `useState(true)` to `useState(false)` for loading initial state
3. Add `if (!enabled) return;` guard at start of useEffect, before the `setLoading(true)` call
4. Add `enabled` to the useEffect dependency array

- [ ] **Step 1: Update `useStudyPerformanceMetrics.js`**

Replace entire file content:
```js
import { useEffect, useState } from "react";
import { fetchStudyPerformance } from "../services/studyAnalysisService";

export function useStudyPerformanceMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchStudyPerformance(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 2: Update `useStudyUxMetrics.js`**

Replace entire file content:
```js
import { useEffect, useState } from "react";
import { fetchStudyQuestionnaires } from "../services/studyAnalysisService";

export function useStudyUxMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchStudyQuestionnaires(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 3: Update `useStudyEyeTrackingMetrics.js`**

Replace entire file content:
```js
import { useEffect, useState } from "react";
import { fetchStudyEyeTracking } from "../services/studyAnalysisService";

export function useStudyEyeTrackingMetrics(studyId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studyId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchStudyEyeTracking(studyId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [studyId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 4: Update `usePerformanceMetrics.js`**

Replace entire file content:
```js
import { useEffect, useState } from "react";
import { fetchPerformanceMetrics } from "../services/performanceMetrics";

export function usePerformanceMetrics(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchPerformanceMetrics(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 5: Update `useUxMetrics.js`**

Replace entire file content:
```js
import { useState, useEffect } from "react";
import { fetchUxMetrics } from "../services/uxMetricsService";

export function useUxMetrics(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchUxMetrics(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 6: Update `useEyeTrackingMetrics.js`**

Replace entire file content:
```js
import { useEffect, useState } from "react";
import { fetchExperimentEyeTracking } from "../services/eyeTrackingService";

export function useEyeTrackingMetrics(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentEyeTracking(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 7: Lint check**

Run: `npm run lint`
Expected: No new errors (existing callers without `enabled` arg still get `true` as default)

- [ ] **Step 8: Commit**

```bash
git add src/features/Analysis/hooks/useStudyPerformanceMetrics.js src/features/Analysis/hooks/useStudyUxMetrics.js src/features/Analysis/hooks/useStudyEyeTrackingMetrics.js src/features/Analysis/hooks/usePerformanceMetrics.js src/features/Analysis/hooks/useUxMetrics.js src/features/Analysis/hooks/useEyeTrackingMetrics.js
git commit -m "feat: add enabled flag to all analysis hooks for lazy loading"
```

---

### Task 4: Create 3 New Frontend Hooks + Service Functions

**Files:**
- Modify: `src/features/Analysis/services/eyeTrackingService.js` (add 3 fetch functions)
- Create: `src/features/Analysis/hooks/useEyeTrackingPhases.js`
- Create: `src/features/Analysis/hooks/useEyeTrackingTransitions.js`
- Create: `src/features/Analysis/hooks/usePPI.js`

- [ ] **Step 1: Add 3 fetch functions to `eyeTrackingService.js`**

Append to `src/features/Analysis/services/eyeTrackingService.js`:
```js
export async function fetchExperimentEyeTrackingPhases(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/phases`);
    if (!res.ok) throw new Error(`Failed to fetch ET phases: ${res.status}`);
    return res.json();
}

export async function fetchExperimentEyeTrackingTransitions(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/eyetracking/transitions`);
    if (!res.ok) throw new Error(`Failed to fetch ET transitions: ${res.status}`);
    return res.json();
}

export async function fetchExperimentPPI(experimentId) {
    const res = await fetch(`/api/analysis/experiment/${experimentId}/ppi`);
    if (!res.ok) throw new Error(`Failed to fetch PPI: ${res.status}`);
    return res.json();
}
```

- [ ] **Step 2: Create `useEyeTrackingPhases.js`**

Create file `src/features/Analysis/hooks/useEyeTrackingPhases.js`:
```js
import { useEffect, useState } from "react";
import { fetchExperimentEyeTrackingPhases } from "../services/eyeTrackingService";

export function useEyeTrackingPhases(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentEyeTrackingPhases(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 3: Create `useEyeTrackingTransitions.js`**

Create file `src/features/Analysis/hooks/useEyeTrackingTransitions.js`:
```js
import { useEffect, useState } from "react";
import { fetchExperimentEyeTrackingTransitions } from "../services/eyeTrackingService";

export function useEyeTrackingTransitions(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentEyeTrackingTransitions(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 4: Create `usePPI.js`**

Create file `src/features/Analysis/hooks/usePPI.js`:
```js
import { useEffect, useState } from "react";
import { fetchExperimentPPI } from "../services/eyeTrackingService";

export function usePPI(experimentId, enabled = true) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!experimentId || !enabled) return;
        setLoading(true);
        setError(null);
        fetchExperimentPPI(experimentId)
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [experimentId, enabled]);

    return { data, loading, error };
}
```

- [ ] **Step 5: Lint check**

Run: `npm run lint`
Expected: No errors

- [ ] **Step 6: Commit**

```bash
git add src/features/Analysis/services/eyeTrackingService.js src/features/Analysis/hooks/useEyeTrackingPhases.js src/features/Analysis/hooks/useEyeTrackingTransitions.js src/features/Analysis/hooks/usePPI.js
git commit -m "feat: add eyetracking phases/transitions and PPI hooks and service functions"
```

---

### Task 5: PlaceholderChart Component + ExperimentAnalyseTabs CSS Refactor

**Files:**
- Create: `src/features/Analysis/components/shared/PlaceholderChart.jsx`
- Modify: `src/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx`

- [ ] **Step 1: Create `PlaceholderChart.jsx`**

Create file `src/features/Analysis/components/shared/PlaceholderChart.jsx`:
```jsx
import React from "react";

export default function PlaceholderChart({ label }) {
    return (
        <div className="border border-dashed border-gray-600 rounded-xl p-6 text-center text-gray-500 my-4">
            <div className="text-sm">{label}</div>
        </div>
    );
}
```

- [ ] **Step 2: Refactor `ExperimentAnalyseTabs.jsx`**

Replace entire file content:
```jsx
import React, { useState } from "react";

export function ExperimentAnalyseTabs({ tabs, defaultKey, onTabChange, children }) {
    const [activeKey, setActiveKey] = useState(defaultKey ?? tabs[0].key);

    function handleClick(key) {
        setActiveKey(key);
        onTabChange?.(key);
    }

    return (
        <div>
            <div className="flex gap-2 mb-6 flex-wrap">
                {tabs.map(tab => (
                    <button
                        key={tab.key}
                        onClick={() => handleClick(tab.key)}
                        className={`px-4 py-2 rounded transition-colors ${
                            activeKey === tab.key
                                ? "bg-blue-700 text-white"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            {React.Children.map(children, child =>
                React.cloneElement(child, { isActive: child.props.tabKey === activeKey })
            )}
        </div>
    );
}

export function TabPanel({ tabKey: _tabKey, children, isActive }) {
    return <div className={isActive ? "" : "hidden"}>{children}</div>;
}
// Note: tabKey is prefixed with _ to satisfy ESLint no-unused-vars.
// The parent reads child.props.tabKey directly — it never needs to be used inside TabPanel.
```

**Important:** `isActive` is consumed by `TabPanel` and never spread to a DOM element, so React will not warn about unknown DOM props. `tabKey` is also only read by the parent's `React.Children.map`, not spread to DOM.

- [ ] **Step 3: Lint check**

Run: `npm run lint`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add src/features/Analysis/components/shared/PlaceholderChart.jsx src/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx
git commit -m "feat: add PlaceholderChart and refactor ExperimentAnalyseTabs to CSS visibility"
```

---

## Chunk 3: Page Implementations

### Task 6: AnalysisPage — Cross-Study Overview

**Files:**
- Replace: `src/features/Analysis/AnalysisPage.jsx`

**Context:** `useStudies()` is from `@/features/study/hooks/useStudies.js`, returns `{ studies, loading, error }`. Studies have shape `{ study_id, status, config: { name } }`. `fetchStudyPerformance` is in `services/studyAnalysisService.js`, returns `{ performance: { by_condition: { [condition]: { total_mean, total_std, n } } } }`. `CrossStudyChart` expects `data = { conditions: { [label]: { mean, ci_lower, ci_upper, n } }, baseline_ms }`.

- [ ] **Step 1: Replace `AnalysisPage.jsx`**

Replace entire file content:
```jsx
import React, { useState } from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { useStudies } from "@/features/study/hooks/useStudies.js";
import { fetchStudyPerformance } from "@/features/Analysis/services/studyAnalysisService.js";
import CrossStudyChart from "@/features/Analysis/components/CrossStudyChart.jsx";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";

const breadcrumbItems = [
    { label: "Studienübersicht", to: "/" },
    { label: "Studien-Meta-Analyse" },
];

function aggregateStudyPerformance(studyId, studyName, performanceData) {
    const byCondition = performanceData?.performance?.by_condition;
    if (!byCondition) return null;

    const conditions = Object.values(byCondition);
    const nTotal = conditions.reduce((sum, c) => sum + (c.n ?? 0), 0);
    if (nTotal === 0) return null;

    // Weighted mean across all conditions
    const weightedMean = conditions.reduce((sum, c) => sum + (c.total_mean ?? 0) * (c.n ?? 0), 0) / nTotal;
    // Weighted std
    const weightedStd = Math.sqrt(
        conditions.reduce((sum, c) => sum + Math.pow(c.total_std ?? 0, 2) * (c.n ?? 0), 0) / nTotal
    );
    const margin = 1.96 * (weightedStd / Math.sqrt(nTotal));

    return {
        label: studyName,
        mean: parseFloat(weightedMean.toFixed(3)),
        ci_lower: parseFloat(Math.max(0, weightedMean - margin).toFixed(3)),
        ci_upper: parseFloat((weightedMean + margin).toFixed(3)),
        n: nTotal,
    };
}

export default function AnalysisPage() {
    const { studies, loading: studiesLoading, error: studiesError } = useStudies();
    const [selectedIds, setSelectedIds] = useState(new Set());
    const [baselineMs, setBaselineMs] = useState(300);
    const [chartData, setChartData] = useState(null);
    const [comparing, setComparing] = useState(false);
    const [compareError, setCompareError] = useState(null);

    const activeStudies = (studies || []).filter(s => s.status !== "Entwurf");

    function toggleStudy(id) {
        setSelectedIds(prev => {
            const next = new Set(prev);
            next.has(id) ? next.delete(id) : next.add(id);
            return next;
        });
    }

    async function handleCompare() {
        setComparing(true);
        setCompareError(null);
        setChartData(null);
        try {
            const results = await Promise.all(
                [...selectedIds].map(id =>
                    fetchStudyPerformance(id)
                        .then(data => ({ id, data }))
                        .catch(() => ({ id, data: null }))
                )
            );
            const conditions = {};
            const failedStudies = [];
            for (const { id, data } of results) {
                const study = activeStudies.find(s => s.study_id === id);
                const label = study?.config?.name || `Studie ${id}`;
                const agg = aggregateStudyPerformance(id, label, data);
                if (agg) {
                    conditions[agg.label] = { mean: agg.mean, ci_lower: agg.ci_lower, ci_upper: agg.ci_upper, n: agg.n };
                } else {
                    failedStudies.push(label);
                }
            }
            // Note: null values are NOT stored in conditions — CrossStudyChart accesses stats.mean directly
            // and would throw a TypeError if stats is null. Failed studies are tracked separately.
            setChartData({ conditions, baseline_ms: baselineMs, failedStudies });
        } catch (err) {
            setCompareError(err.message);
        } finally {
            setComparing(false);
        }
    }

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Studien-Meta-Analyse</h1>

            {/* Study selection panel */}
            <div className="bg-gray-800 rounded-xl p-4 mb-6">
                <h2 className="text-lg font-semibold mb-3">Studien auswählen</h2>
                {studiesLoading && <LoadingSpinner message="Studien laden..." />}
                {studiesError && <ErrorMessage error={studiesError} />}
                {!studiesLoading && activeStudies.length === 0 && (
                    <p className="text-gray-400">Keine abgeschlossenen oder aktiven Studien vorhanden.</p>
                )}
                <div className="flex flex-col gap-2">
                    {activeStudies.map(study => (
                        <label key={study.study_id} className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedIds.has(study.study_id)}
                                onChange={() => toggleStudy(study.study_id)}
                                className="w-4 h-4"
                            />
                            <span>{study.config?.name || `Studie ${study.study_id}`}</span>
                            <span className="text-xs text-gray-400">({study.status})</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Baseline input */}
            <div className="flex items-center gap-3 mb-6">
                <label className="text-sm text-gray-300">Baseline (ms):</label>
                <input
                    type="number"
                    value={baselineMs}
                    onChange={e => setBaselineMs(Number(e.target.value))}
                    className="w-24 px-2 py-1 rounded bg-gray-700 border border-gray-600 text-white text-sm"
                    min={0}
                />
            </div>

            <button
                onClick={handleCompare}
                disabled={selectedIds.size < 2 || comparing}
                className="px-6 py-2 rounded bg-blue-700 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-600 mb-6"
            >
                {comparing ? "Vergleiche..." : "Studien vergleichen"}
            </button>
            {selectedIds.size < 2 && (
                <p className="text-xs text-gray-500 mb-4">Mindestens 2 Studien auswählen</p>
            )}

            {compareError && <ErrorMessage error={compareError} />}

            {comparing && <LoadingSpinner message="Daten werden geladen..." />}

            {chartData && !comparing && (
                <div>
                    <DescriptiveOnlyWarning message="Deskriptiver Vergleich — kein inferenzieller Test (unterschiedliche Teilnehmer je Studie)" />
                    <div className="mt-4">
                        <CrossStudyChart data={chartData} metric="Transfer Duration (ms)" />
                    </div>
                </div>
            )}
        </div>
    );
}
```

- [ ] **Step 2: Lint check**

Run: `npm run lint`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/AnalysisPage.jsx
git commit -m "feat: implement AnalysisPage as cross-study overview with study selection and forest plot"
```

---

### Task 7: StudyAnalysisPage — Lazy Loading + Inferential Panel + Export Tab

**Files:**
- Replace: `src/features/Analysis/StudyAnalysisPage.jsx`

**Context:** Current file has combined loading guard (lines 34–82) that blocks entire page. Remove it. Add `loadedTabs` Set, `handleTabChange`, and `export` tab. Add `InferenzPanel` inline component that renders inferential results from data already returned by the study endpoints.

- [ ] **Step 1: Replace `StudyAnalysisPage.jsx`**

Replace entire file content:
```jsx
import React, { useState } from "react";
import { useParams } from "react-router-dom";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import { useStudyPerformanceMetrics } from "@/features/Analysis/hooks/useStudyPerformanceMetrics.js";
import { useStudyUxMetrics } from "@/features/Analysis/hooks/useStudyUxMetrics.js";
import { useStudyEyeTrackingMetrics } from "@/features/Analysis/hooks/useStudyEyeTrackingMetrics.js";
import StudyPerformanceCharts from "@/features/Analysis/components/study/StudyPerformanceCharts.jsx";
import StudyQuestionnaireCharts from "@/features/Analysis/components/study/StudyQuestionnaireCharts.jsx";
import StudyEyeTrackingCharts from "@/features/Analysis/components/study/StudyEyeTrackingCharts.jsx";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import InferentialResultBadge from "@/features/Analysis/components/shared/InferentialResultBadge.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";
import { downloadStudyCsv, downloadStudyXlsx } from "@/features/Analysis/services/inferentialAnalysisService.js";

const TABS = [
    { key: "performance", label: "Performance" },
    { key: "questionnaires", label: "Fragebögen" },
    { key: "eyetracking", label: "Eye-Tracking" },
    { key: "export", label: "Export" },
];

function InferenzPanel({ inferential, label }) {
    if (!inferential || Object.keys(inferential).length === 0) return null;
    const entries = Object.entries(inferential);
    const hasAny = entries.some(([, v]) => v !== null);
    if (!hasAny) {
        return (
            <DescriptiveOnlyWarning message="Zu wenig Daten für inferenzielle Tests (n < 3 pro Bedingung)." />
        );
    }
    return (
        <div className="mt-6">
            <h3 className="text-base font-semibold mb-3">{label || "Inferenzielle Analyse"}</h3>
            <div className="flex flex-col gap-3">
                {entries.map(([key, result]) => (
                    <div key={key} className="bg-gray-800 rounded-lg p-3">
                        <div className="text-sm text-gray-400 mb-1">{key}</div>
                        <InferentialResultBadge result={result} />
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function StudyAnalysisPage() {
    const { studyId } = useParams();
    const [loadedTabs, setLoadedTabs] = useState(new Set(["performance"]));
    const [downloading, setDownloading] = useState(false);
    const [downloadError, setDownloadError] = useState(null);

    const { data: studyPerformance, loading: perfLoading, error: perfError } =
        useStudyPerformanceMetrics(studyId, true);
    const { data: studyQuestionnaires, loading: uxLoading, error: uxError } =
        useStudyUxMetrics(studyId, loadedTabs.has("questionnaires"));
    const { data: studyEyeTracking, loading: etLoading, error: etError } =
        useStudyEyeTrackingMetrics(studyId, loadedTabs.has("eyetracking"));

    function handleTabChange(tabKey) {
        setLoadedTabs(prev => new Set([...prev, tabKey]));
    }

    async function handleDownload(type) {
        setDownloading(true);
        setDownloadError(null);
        try {
            if (type === "csv") await downloadStudyCsv(studyId);
            else await downloadStudyXlsx(studyId);
        } catch (err) {
            setDownloadError(err.message);
        } finally {
            setDownloading(false);
        }
    }

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Studien-Analyse" },
    ];

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Studien-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="performance" onTabChange={handleTabChange}>
                <TabPanel tabKey="performance">
                    {perfLoading && <LoadingSpinner message="Performance-Daten laden..." />}
                    {perfError && <ErrorMessage error={perfError} />}
                    {studyPerformance && (
                        <>
                            <StudyPerformanceCharts chartData={studyPerformance} />
                            <InferenzPanel
                                inferential={studyPerformance?.performance?.inferential}
                                label="Inferenzielle Analyse — Transfer-Dauer"
                            />
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="questionnaires">
                    {uxLoading && <LoadingSpinner message="Fragebogen-Daten laden..." />}
                    {uxError && <ErrorMessage error={uxError} />}
                    {studyQuestionnaires && (
                        <>
                            <StudyQuestionnaireCharts chartData={studyQuestionnaires} />
                            {studyQuestionnaires?.questionnaires &&
                                Object.entries(studyQuestionnaires.questionnaires).map(([qName, qData]) => (
                                    <InferenzPanel
                                        key={qName}
                                        inferential={qData?.inferential}
                                        label={`Inferenzielle Analyse — ${qName}`}
                                    />
                                ))
                            }
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="eyetracking">
                    {etLoading && <LoadingSpinner message="Eye-Tracking-Daten laden..." />}
                    {etError && <ErrorMessage error={etError} />}
                    {studyEyeTracking && (
                        <>
                            <StudyEyeTrackingCharts chartData={studyEyeTracking} />
                            <InferenzPanel
                                inferential={studyEyeTracking?.inferential}
                                label="Inferenzielle Analyse — AOI Dwell-Time"
                            />
                        </>
                    )}
                </TabPanel>
                <TabPanel tabKey="export">
                    <div className="mt-4">
                        <h2 className="text-lg font-semibold mb-4">Daten exportieren</h2>
                        {downloadError && <ErrorMessage error={downloadError} />}
                        <div className="flex gap-4 flex-wrap">
                            <button
                                onClick={() => handleDownload("csv")}
                                disabled={downloading}
                                className="px-6 py-2 rounded bg-green-700 text-white disabled:opacity-40 hover:bg-green-600"
                            >
                                {downloading ? "Wird exportiert..." : "CSV herunterladen"}
                            </button>
                            <button
                                onClick={() => handleDownload("xlsx")}
                                disabled={downloading}
                                className="px-6 py-2 rounded bg-blue-700 text-white disabled:opacity-40 hover:bg-blue-600"
                            >
                                {downloading ? "Wird exportiert..." : "Excel herunterladen"}
                            </button>
                        </div>
                        <p className="text-xs text-gray-500 mt-3">
                            Exportiert alle Handover-Daten der Studie {studyId}.
                        </p>
                    </div>
                </TabPanel>
            </ExperimentAnalyseTabs>
        </div>
    );
}
```

- [ ] **Step 2: Lint check**

Run: `npm run lint`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/StudyAnalysisPage.jsx
git commit -m "feat: refactor StudyAnalysisPage with lazy tabs, inferential panel, and export tab"
```

---

### Task 8: ExperimentAnalysisPage — Full Descriptive Restructure

**Files:**
- Replace: `src/features/Analysis/ExperimentAnalysisPage.jsx`

**Context:** Current file (line 57) has a combined loading guard blocking the page. Remove `useHandovers`, `computeMetricsPerTrial` (unused). Add 5-tab layout with lazy loading. ET-Tab uses 3 new hooks. All tabs are descriptive only.

- [ ] **Step 1: Replace `ExperimentAnalysisPage.jsx`**

Replace entire file content:
```jsx
import React, { useState } from "react";
import Breadcrumbs from "@/components/Breadcrumbs.jsx";
import { useParams } from "react-router-dom";
import { useExperiment } from "@/features/Analysis/hooks/useExperiment.js";
import ExperimentDetails from "@/features/Analysis/components/experiment/ExperimentDetails.jsx";
import { useParticipantsForExperiment } from "@/features/overview/hooks/useParticipantsForExperiment.js";
import QuestionnaireCharts from "@/features/Analysis/components/experiment/QuestionnaireCharts.jsx";
import PerformanceCharts from "@/features/Analysis/components/experiment/PerformanceCharts.jsx";
import EyeTrackingCharts from "@/features/Analysis/components/experiment/EyeTrackingCharts.jsx";
import ComparisonCharts from "@/features/Analysis/components/experiment/ComparisonCharts.jsx";
import { ExperimentAnalyseTabs, TabPanel } from "@/features/Analysis/components/experiment/ExperimentAnalyseTabs.jsx";
import { useUxMetrics } from "@/features/Analysis/hooks/useUxMetrics.js";
import { usePerformanceMetrics } from "@/features/Analysis/hooks/usePerformanceMetrics.js";
import { useEyeTrackingMetrics } from "@/features/Analysis/hooks/useEyeTrackingMetrics.js";
import { useEyeTrackingPhases } from "@/features/Analysis/hooks/useEyeTrackingPhases.js";
import { useEyeTrackingTransitions } from "@/features/Analysis/hooks/useEyeTrackingTransitions.js";
import { usePPI } from "@/features/Analysis/hooks/usePPI.js";
import LoadingSpinner from "@/features/Analysis/components/shared/LoadingSpinner.jsx";
import ErrorMessage from "@/features/Analysis/components/shared/ErrorMessage.jsx";
import DescriptiveOnlyWarning from "@/features/Analysis/components/shared/DescriptiveOnlyWarning.jsx";
import PlaceholderChart from "@/features/Analysis/components/shared/PlaceholderChart.jsx";

const TABS = [
    { key: "details", label: "Experiment Info" },
    { key: "performance", label: "Performance" },
    { key: "eyetracking", label: "Eye-Tracking" },
    { key: "ux", label: "Fragebögen / UX" },
    { key: "compare", label: "Vergleiche" },
];

const DESCRIPTIVE_WARNING =
    "Deskriptive Analyse eines Messdurchgangs. Inferenzielle Auswertung über alle Experimente → Studien-Analyse.";

export default function ExperimentAnalysisPage() {
    const { studyId, experimentId } = useParams();
    const [loadedTabs, setLoadedTabs] = useState(new Set(["details"]));

    const { experiment, loading: expLoading, error: expError } = useExperiment(experimentId);
    const { participants, loading: partLoading } = useParticipantsForExperiment(experimentId);

    const { data: uxMetrics, loading: uxLoading, error: uxError } =
        useUxMetrics(experimentId, loadedTabs.has("ux") || loadedTabs.has("compare"));
    const { data: performanceMetrics, loading: perfLoading, error: perfError } =
        usePerformanceMetrics(experimentId, loadedTabs.has("performance") || loadedTabs.has("compare"));
    const { data: eyeTrackingData, loading: etLoading, error: etError } =
        useEyeTrackingMetrics(experimentId, loadedTabs.has("eyetracking"));
    const { data: etPhasesData, loading: phasesLoading, error: phasesError } =
        useEyeTrackingPhases(experimentId, loadedTabs.has("eyetracking"));
    // etTransitionsData prefixed with _ — data is fetched now but rendered in Session B (TransitionSankey)
    const { data: _etTransitionsData, loading: transLoading, error: transError } =
        useEyeTrackingTransitions(experimentId, loadedTabs.has("eyetracking"));
    const { data: ppiData, loading: ppiLoading, error: ppiError } =
        usePPI(experimentId, loadedTabs.has("eyetracking"));

    function handleTabChange(tabKey) {
        if (tabKey === "compare") {
            setLoadedTabs(prev => new Set([...prev, tabKey, "performance", "ux"]));
        } else {
            setLoadedTabs(prev => new Set([...prev, tabKey]));
        }
    }

    const breadcrumbItems = [
        { label: "Studienübersicht", to: "/" },
        { label: "Studie", to: `/study/${studyId}/experiments` },
        { label: "Experiment-Analyse" },
    ];

    const experimentDetails = experiment ? {
        study_id: experiment.study_id,
        experiment_id: experiment.experiment_id,
        researcher: experiment.researcher,
        description: experiment.description,
        created_at: experiment.created_at,
        started_at: experiment.started_at,
        completed_at: experiment.completed_at,
    } : null;

    return (
        <div className="p-6 relative bg-gray-900 min-h-screen text-gray-100">
            <Breadcrumbs items={breadcrumbItems} styled={true} className="mb-6" />
            <h1 className="text-2xl font-bold mb-6">Experiment-Analyse</h1>
            <ExperimentAnalyseTabs tabs={TABS} defaultKey="details" onTabChange={handleTabChange}>

                {/* === DETAILS === */}
                <TabPanel tabKey="details">
                    {expLoading && <LoadingSpinner message="Experiment laden..." />}
                    {expError && <ErrorMessage error={expError} />}
                    {experimentDetails && (
                        <ExperimentDetails experimentDetails={experimentDetails} participants={participants} />
                    )}
                </TabPanel>

                {/* === PERFORMANCE === */}
                <TabPanel tabKey="performance">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {perfLoading && <LoadingSpinner message="Performance-Daten laden..." />}
                    {perfError && <ErrorMessage error={perfError} />}
                    {performanceMetrics && <PerformanceCharts chartData={performanceMetrics} />}
                    {/* SESSION B: PerformanceViolin */}
                    <PlaceholderChart label="Violinplot pro Bedingung (kommt in Session B)" />
                    {/* SESSION B: ErrorRateBar */}
                    <PlaceholderChart label="Fehlerrate pro Bedingung (kommt in Session B)" />
                </TabPanel>

                {/* === EYE-TRACKING === */}
                <TabPanel tabKey="eyetracking">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {etLoading && <LoadingSpinner message="Eye-Tracking-Daten laden..." />}
                    {etError && <ErrorMessage error={etError} />}
                    {eyeTrackingData && <EyeTrackingCharts chartData={eyeTrackingData} />}

                    {/* Phase + Transition data loading states */}
                    {(phasesLoading || transLoading) && <LoadingSpinner message="Phasen & Transitionen laden..." />}
                    {phasesError && <ErrorMessage error={phasesError} />}
                    {transError && <ErrorMessage error={transError} />}
                    {/* etTransitionsData is fetched here and will be consumed by Session B's TransitionSankey */}

                    {/* PPI display */}
                    {ppiLoading && <LoadingSpinner message="PPI berechnen..." />}
                    {ppiError && <ErrorMessage error={ppiError} />}
                    {ppiData && ppiData.by_trial && (
                        <div className="mt-4 bg-gray-800 rounded-xl p-4">
                            <h3 className="text-sm font-semibold mb-2">Proaktiver Planungsindex (PPI)</h3>
                            <p className="text-xs text-gray-400 mb-2">
                                Anteil der Geber-Blickzeit auf den Aufgabenbereich (environment) in Phase 3.
                                Hoher PPI (&gt;30%) = automatisch-haptische Übergabe.
                            </p>
                            <div className="flex flex-wrap gap-3">
                                {Object.values(ppiData.by_trial).map(trial => (
                                    <div key={trial.trial_number} className="text-xs bg-gray-700 rounded px-3 py-2">
                                        <div className="font-medium">Trial {trial.trial_number}</div>
                                        <div>Geber: {trial.ppi_giver !== null ? `${trial.ppi_giver.toFixed(1)}%` : "–"}</div>
                                        <div>Empfänger: {trial.ppi_receiver !== null ? `${trial.ppi_receiver.toFixed(1)}%` : "–"}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="AOI × Phasen-Heatmap (kommt in Session B)" />
                    <PlaceholderChart label="Blickpfad-Sankey (kommt in Session B)" />
                    <PlaceholderChart label="Sakkaden-Rate pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="Gaze-Timeline (kommt in Session B)" />
                    <PlaceholderChart label="PPI-Balkendiagramm pro Bedingung (kommt in Session B)" />
                </TabPanel>

                {/* === UX / QUESTIONNAIRES === */}
                <TabPanel tabKey="ux">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {uxLoading && <LoadingSpinner message="Fragebogen-Daten laden..." />}
                    {uxError && <ErrorMessage error={uxError} />}
                    {uxMetrics && <QuestionnaireCharts chartData={uxMetrics} />}
                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="NASA-TLX Subskalen pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="SUS-Score pro Bedingung (kommt in Session B)" />
                    <PlaceholderChart label="AttrakDiff2 Portfolio-Matrix (kommt in Session B)" />
                    <PlaceholderChart label="AttrakDiff2 Subskalen-Radar (kommt in Session B)" />
                </TabPanel>

                {/* === COMPARE === */}
                <TabPanel tabKey="compare">
                    <DescriptiveOnlyWarning message={DESCRIPTIVE_WARNING} />
                    {(perfLoading || uxLoading) && <LoadingSpinner message="Vergleichsdaten laden..." />}
                    {(perfError || uxError) && <ErrorMessage error={perfError || uxError} />}
                    {performanceMetrics && uxMetrics && (
                        <ComparisonCharts uxMetrics={uxMetrics} performanceMetrics={performanceMetrics} />
                    )}
                    {/* SESSION B placeholders */}
                    <PlaceholderChart label="Korrelationsmatrix (kommt in Session B)" />
                </TabPanel>

            </ExperimentAnalyseTabs>
        </div>
    );
}
```

- [ ] **Step 2: Lint check**

Run: `npm run lint`
Expected: No errors (all imports are valid after previous tasks)

- [ ] **Step 3: Commit**

```bash
git add src/features/Analysis/ExperimentAnalysisPage.jsx
git commit -m "feat: restructure ExperimentAnalysisPage with lazy tabs, descriptive analysis, and Session B placeholders"
```

---

## Chunk 4: Cleanup

### Task 9: Delete Orphaned Files

**Files:**
- Delete: `src/features/Analysis/pages/AnalysisDashboard.jsx`
- Delete: `src/features/Analysis/components/PerformanceChart.jsx`
- Delete: `src/features/Analysis/components/EyeTrackingChart.jsx`

**Verification before deleting:** Confirm nothing imports these files.

- [ ] **Step 1: Verify no imports**

Run each:
```bash
grep -r "AnalysisDashboard" src/ --include="*.jsx" --include="*.js"
grep -r "components/PerformanceChart" src/ --include="*.jsx" --include="*.js"
grep -r "components/EyeTrackingChart" src/ --include="*.jsx" --include="*.js"
```
Expected: No output (these files are only self-contained; `PerformanceChart.jsx` and `EyeTrackingChart.jsx` at `components/` level are different from `components/experiment/PerformanceCharts.jsx` and `EyeTrackingCharts.jsx` which are kept)

- [ ] **Step 2: Delete the files**

```bash
rm src/features/Analysis/pages/AnalysisDashboard.jsx
rm src/features/Analysis/components/PerformanceChart.jsx
rm src/features/Analysis/components/EyeTrackingChart.jsx
```

- [ ] **Step 3: Lint check**

Run: `npm run lint`
Expected: No errors related to removed files

- [ ] **Step 4: Commit**

```bash
git add -A src/features/Analysis/pages/AnalysisDashboard.jsx src/features/Analysis/components/PerformanceChart.jsx src/features/Analysis/components/EyeTrackingChart.jsx
git commit -m "chore: delete orphaned AnalysisDashboard and self-fetching chart components"
```

---

### Task 10: Final Verification

- [ ] **Step 1: Run full backend test suite**

Run: `uv run pytest Backend/tests/ -v`
Expected: All PASS

- [ ] **Step 2: Run frontend lint**

Run: `npm run lint`
Expected: No errors

- [ ] **Step 3: Manual smoke test (optional if dev server available)**

Start: `uv run fastapi dev Backend/app.py` and `npm run dev`

Verify:
1. `/analysis` loads → shows study checkboxes, compare button disabled with < 2 selected
2. `/study/1/analysis` loads immediately → Performance tab shows charts, no spinner blocking
3. Switch to Fragebögen tab → spinner appears briefly, then data
4. Export tab → CSV/Excel buttons functional
5. `/study/1/experiment/1/analysis` loads immediately → Details tab shows experiment info
6. Performance tab → charts + placeholder cards visible
7. ET tab → existing chart + PPI cards (empty if no data) + placeholders
8. Compare tab → triggers both performance + UX load

- [ ] **Step 4: Final commit / tag**

```bash
git add -A
git status  # ensure only expected files
git commit -m "chore: session A analysis UI integration complete"
```
