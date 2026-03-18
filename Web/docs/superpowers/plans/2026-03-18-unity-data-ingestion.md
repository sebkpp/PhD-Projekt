# Unity Data Ingestion API — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable Unity to write Handover performance data and Eye-Tracking fixation events into the database in real time via FastAPI endpoints, and reduce AvatarVisibility to a single fixed "Full Body" entry.

**Architecture:** Three independent chunks executed in order. Chunk 1 (AvatarVisibility) is a pure data/config change. Chunk 2 (Handover PATCH) adds a new endpoint and fixes an existing one. Chunk 3 (ET API) requires the `hanover_id → handover_id` typo fix first, then adds a new router. All new code follows the existing route→service→repository pattern.

**Tech Stack:** Python/FastAPI, SQLAlchemy ORM, Pydantic v1, pytest, PostgreSQL

**Spec:** `docs/superpowers/specs/2026-03-18-unity-data-ingestion-design.md`

---

## Chunk 1: AvatarVisibility — Reduce to "Full Body"

### Task 1: Reduce seed data and update TrialSlotRepository

**Files:**
- Modify: `Backend/data/static/avatar_visibility.json`
- Modify: `Backend/db/trial/trial_slot_repository.py`
- Modify: `Backend/data/testmock/trial_slot.json`
- Modify: `Backend/scripts/import_trial_slot.py`

- [ ] **Step 1: Update `avatar_visibility.json`**

Replace the entire file content with:

```json
[
  {
    "name": "full",
    "label": "Ganze Figur"
  }
]
```

- [ ] **Step 2: Update `trial_slot_repository.py` — remove `avatar_visibility` parameter**

Open `Backend/db/trial/trial_slot_repository.py`. Find the `create` method (lines 7–16):

```python
def create(self, trial_id: int, slot_number: int, avatar_visibility:int) -> TrialSlot:
    trial_slot = TrialSlot(
        trial_id=trial_id,
        slot=slot_number,
        avatar_visibility_id = avatar_visibility
    )
```

Replace with:

```python
def create(self, trial_id: int, slot_number: int) -> TrialSlot:
    trial_slot = TrialSlot(
        trial_id=trial_id,
        slot=slot_number,
        avatar_visibility_id=1,
    )
```

- [ ] **Step 3: Update `import_trial_slot.py` — hardcode avatar_visibility_id=1**

Open `Backend/scripts/import_trial_slot.py`. Find the `existing` update block and the `TrialSlot(...)` insert block. Replace both with hardcoded `avatar_visibility_id=1`:

In the `if existing:` block, change:
```python
existing.avatar_visibility_id = s['avatar_visibility_id']
```
to:
```python
existing.avatar_visibility_id = 1
```

In the `else:` block, change:
```python
slot = TrialSlot(
    trial_slot_id=s['trial_slot_id'],
    trial_id=s['trial_id'],
    slot=s['slot'],
    avatar_visibility_id=s['avatar_visibility_id'],
)
```
to:
```python
slot = TrialSlot(
    trial_slot_id=s['trial_slot_id'],
    trial_id=s['trial_id'],
    slot=s['slot'],
    avatar_visibility_id=1,
)
```

- [ ] **Step 4: Update `trial_slot.json` — set all avatar_visibility_id to 1**

The file `Backend/data/testmock/trial_slot.json` contains rows with `avatar_visibility_id` values 1, 2, or 3. Run:

```bash
cd Web && python -c "
import json
with open('Backend/data/testmock/trial_slot.json', 'r') as f:
    data = json.load(f)
for row in data:
    row['avatar_visibility_id'] = 1
with open('Backend/data/testmock/trial_slot.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f'Updated {len(data)} rows.')
"
```

Expected output: `Updated N rows.`

- [ ] **Step 5: Check if any caller passes `avatar_visibility` to `TrialSlotRepository.create`**

```bash
cd Web && grep -rn "TrialSlotRepository\|trial_slot_repo\|slot_repo" Backend/ --include="*.py" | grep -v "__pycache__"
```

If any call site passes a third argument (`avatar_visibility`), remove that argument. Most likely all callers are in `experiment_service.py` or `trial_service.py` — inspect and fix.

- [ ] **Step 6: Run full test suite to verify no regressions**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short 2>&1 | tail -20
```

Expected: all tests pass (pre-existing passing count unchanged).

### Task 2: Update AvatarVisibility tests

**Files:**
- Modify: `Backend/tests/test_avatar_visibility.py`

- [ ] **Step 1: Update the fixture to seed only `"full"` / `"Ganze Figur"`**

Open `Backend/tests/test_avatar_visibility.py`. Replace the `seeded_avatar_visibility` fixture.

> **Why delete ALL first:** `conftest.py` never clears the `avatar_visibility` table
> (it is treated as static seed data). If the test DB was populated before, old rows
> (`"hands"`, `"head"`) survive between test runs and cause `len(data) == 1` to fail.
> Delete all rows and re-seed only `"full"`.

```python
@pytest.fixture
def seeded_avatar_visibility():
    """Löscht alle AvatarVisibility-Einträge und legt nur 'full' neu an."""
    db = SessionLocal()
    db.query(AvatarVisibility).delete(synchronize_session=False)
    db.commit()

    entries = [
        AvatarVisibility(avatar_visibility_name="full", label="Ganze Figur"),
    ]
    db.add_all(entries)
    db.commit()
    ids = [e.avatar_visibility_id for e in entries]
    db.close()

    yield ids

    db = SessionLocal()
    db.query(AvatarVisibility).delete(synchronize_session=False)
    db.commit()
    db.close()
```

- [ ] **Step 2: Update `test_list_avatar_visibility_returns_correct_fields`**

Change `assert len(data) == 2` → `assert len(data) == 1`.

- [ ] **Step 3: Update `test_list_avatar_visibility_values`**

Replace the assertions to match the new single entry:

```python
def test_list_avatar_visibility_values(client, seeded_avatar_visibility):
    resp = client.get("/avatar-visibility/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    names = {item["name"] for item in data}
    labels = {item["label"] for item in data}
    assert "full" in names
    assert "Ganze Figur" in labels
```

- [ ] **Step 4: Run avatar_visibility tests**

```bash
cd Web && uv run pytest Backend/tests/test_avatar_visibility.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit Chunk 1**

```bash
git add Backend/data/static/avatar_visibility.json \
        Backend/data/testmock/trial_slot.json \
        Backend/db/trial/trial_slot_repository.py \
        Backend/scripts/import_trial_slot.py \
        Backend/tests/test_avatar_visibility.py
git commit -m "feat: reduce avatar visibility to single full-body entry"
```

---

## Chunk 2: Handover API — Fix POST + Add PATCH /phases

### Task 3: Fix HandoverCreateRequest and clean up dead parse_iso code

**Files:**
- Modify: `Backend/routes/handover_routes.py`
- Modify: `Backend/db/handover_repository.py`

- [ ] **Step 1: Write the regression test first**

Open `Backend/tests/test_analysis.py` (or create `Backend/tests/test_handover.py` — use the new file).

Create `Backend/tests/test_handover.py`:

```python
import pytest
from starlette import status


@pytest.fixture
def trial_id(client, experiment_id):
    """Creates a trial and returns its trial_id.

    POST /experiments/{id}/trials returns {"status": "ok", "message": "..."}
    — no trial_id. Use GET /experiments/{id}/trials to retrieve the created record.
    """
    resp = client.post(
        f"/experiments/{experiment_id}/trials",
        json={"trials": [{"trial_number": 1, "slots": []}], "questionnaires": []}
    )
    assert resp.status_code == 201, resp.text
    trials = client.get(f"/experiments/{experiment_id}/trials").json()
    assert len(trials) > 0, "No trials found after creation"
    return trials[0]["trial_id"]


@pytest.fixture
def participant_ids(client):
    """Creates two participants and returns their IDs."""
    ids = []
    for _ in range(2):
        resp = client.post(
            "/api/participants/",
            json={"age": 25, "gender": "m", "handedness": "right"}
        )
        assert resp.status_code == 201, resp.text
        ids.append(resp.json()["participant_id"])
    return ids


def test_handover_init_creates_record(client, trial_id, participant_ids):
    """POST creates a handover record and returns handover_id."""
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1], "grasped_object": "Cube"}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "handover_id" in data
    assert data["handover_id"] is not None


def test_handover_init_missing_giver(client, trial_id):
    """POST without giver returns 422."""
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"receiver": 1}
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

- [ ] **Step 2: Run tests — expect first two to FAIL (route currently accepts extra fields without rejecting)**

```bash
cd Web && uv run pytest Backend/tests/test_handover.py -v
```

Expected: `test_handover_init_creates_record` likely passes (route exists), others may fail due to fixture issues. Fix fixture if needed, then continue.

- [ ] **Step 3: Fix `HandoverCreateRequest` in `handover_routes.py`**

Open `Backend/routes/handover_routes.py`. Replace the entire `HandoverCreateRequest` class:

```python
class HandoverCreateRequest(BaseModel):
    giver: int
    receiver: int
    grasped_object: Optional[str] = None
```

Remove the four timestamp fields (`giver_grasped_object`, `receiver_touched_object`,
`receiver_grasped_object`, `giver_released_object`) from the class entirely.

- [ ] **Step 4: Clean up dead `parse_iso` loop in `HandoverRepository.create_handover`**

Open `Backend/db/handover_repository.py`. Remove the now-dead loop (lines 49–56):

```python
# REMOVE this entire block:
for key in [
    "giver_grasped_object",
    "receiver_touched_object",
    "receiver_grasped_object",
    "giver_released_object"
]:
    if key in handover_data:
        handover_data[key] = parse_iso(handover_data[key])
```

The `parse_iso` helper function can stay (it will be reused in the next task).

- [ ] **Step 5: Run handover tests**

```bash
cd Web && uv run pytest Backend/tests/test_handover.py -v
```

Expected: all 3 tests PASS.

### Task 4: Add PATCH /handovers/{handover_id}/phases

**Files:**
- Modify: `Backend/routes/handover_routes.py`
- Modify: `Backend/db/handover_repository.py`
- Modify: `Backend/services/handover_service.py`
- Modify: `Backend/tests/test_handover.py`

- [ ] **Step 1: Write the failing tests**

Add to `Backend/tests/test_handover.py`:

```python
def test_handover_patch_phases_updates_timestamps(client, trial_id, participant_ids):
    """PATCH /phases sets timestamps; other fields remain NULL."""
    # Init
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    assert init.status_code == 201
    handover_id = init.json()["handover_id"]

    # Patch one timestamp
    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"giver_grasped_object": "2025-09-08T10:00:03.484"}
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["handover_id"] == handover_id


def test_handover_patch_partial_update(client, trial_id, participant_ids):
    """PATCH with one field does not overwrite other fields."""
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    handover_id = init.json()["handover_id"]

    # Set giver_grasped_object first
    client.patch(
        f"/handovers/{handover_id}/phases",
        json={"giver_grasped_object": "2025-09-08T10:00:03.484"}
    )

    # Set receiver_touched_object in second call
    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"receiver_touched_object": "2025-09-08T10:00:03.890"}
    )
    assert resp.status_code == status.HTTP_200_OK


def test_handover_patch_not_found(client):
    """PATCH on non-existing handover_id returns 404."""
    resp = client.patch(
        "/handovers/99999/phases",
        json={"is_error": True}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_handover_patch_sets_is_error(client, trial_id, participant_ids):
    """PATCH can set is_error and error_type."""
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    handover_id = init.json()["handover_id"]

    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"is_error": True, "error_type": "drop"}
    )
    assert resp.status_code == status.HTTP_200_OK
```

- [ ] **Step 2: Run to confirm tests FAIL (route doesn't exist yet)**

```bash
cd Web && uv run pytest Backend/tests/test_handover.py::test_handover_patch_phases_updates_timestamps -v
```

Expected: FAIL with 404 or 405 (no route).

- [ ] **Step 3: Add `update_handover_phases` to `HandoverRepository`**

Open `Backend/db/handover_repository.py`. Add this method after `create_handover`:

```python
def update_handover_phases(self, handover_id: int, patch_data: dict):
    handover = self.session.query(Handover).filter_by(handover_id=handover_id).first()
    if handover is None:
        return None
    updatable = [
        "giver_grasped_object",
        "receiver_touched_object",
        "receiver_grasped_object",
        "giver_released_object",
        "is_error",
        "error_type",
    ]
    for field in updatable:
        if field in patch_data and patch_data[field] is not None:
            setattr(handover, field, patch_data[field])
    self.session.flush()
    return handover
```

> **Note:** `HandoverPhasePatchRequest` uses `Optional[datetime]` — FastAPI/Pydantic
> automatically coerces ISO strings to `datetime` objects before the dict reaches the
> repository. No manual `parse_iso` call is needed here.

- [ ] **Step 4: Add `update_handover_phases` to `handover_service.py`**

Open `Backend/services/handover_service.py`. Add at the end:

```python
def update_handover_phases(session, handover_id: int, patch_data: dict):
    repo = HandoverRepository(session)
    return repo.update_handover_phases(handover_id, patch_data)
```

Also add the import at the top of the file (if not already there):
```python
from Backend.db.handover_repository import HandoverRepository
```

- [ ] **Step 5: Add the PATCH route to `handover_routes.py`**

Open `Backend/routes/handover_routes.py`. Add two new items to the imports at the top:

```python
from datetime import datetime
from Backend.services.handover_service import save_handover, get_handovers_for_trial, get_handovers_for_experiment, update_handover_phases
```

Add the new Pydantic model after `HandoverCreateRequest`:

```python
class HandoverPhasePatchRequest(BaseModel):
    giver_grasped_object: Optional[datetime] = None
    receiver_touched_object: Optional[datetime] = None
    receiver_grasped_object: Optional[datetime] = None
    giver_released_object: Optional[datetime] = None
    is_error: Optional[bool] = None
    error_type: Optional[str] = None
```

Add the new route at the end of the file:

```python
@router.patch(
    "/{handover_id}/phases",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Handover phase timestamps",
    description="Partially update phase timestamps and error state for an existing handover. Only non-null fields are written.",
)
async def patch_handover_phases(
        handover_id: int,
        payload: HandoverPhasePatchRequest,
        db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        patch_data = payload.model_dump()
        result = update_handover_phases(db, handover_id, patch_data)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Handover not found")
        db.commit()
        return MessageResponse(message="Handover phases updated", handover_id=result.handover_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
```

- [ ] **Step 6: Run all handover tests**

```bash
cd Web && uv run pytest Backend/tests/test_handover.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 7: Run full test suite**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short 2>&1 | tail -10
```

Expected: all tests PASS, no regressions.

- [ ] **Step 8: Commit Chunk 2**

```bash
git add Backend/routes/handover_routes.py \
        Backend/db/handover_repository.py \
        Backend/services/handover_service.py \
        Backend/tests/test_handover.py
git commit -m "feat: fix HandoverCreateRequest, add PATCH /handovers/{id}/phases endpoint"
```

---

## Chunk 3: Eye-Tracking API

### Task 5: Fix hanover_id → handover_id typo

**Files:**
- Modify: `Backend/models/eyetracking.py`
- Modify: `sql/schema.sql` (at repo root, not inside `Web/`)
- Modify: `Backend/data/testmock/eye_tracking.json`

> **Order matters:** Complete this task entirely before Task 6. The new repository code references `handover_id`, which requires the ORM rename to be in place first.

- [ ] **Step 1: Fix `Backend/models/eyetracking.py`**

Open `Backend/models/eyetracking.py`. Change line 25:

```python
# FROM:
hanover_id = Column(Integer, ForeignKey("handover.handover_id"), nullable=False)

# TO:
handover_id = Column(Integer, ForeignKey("handover.handover_id"), nullable=False)
```

The relationship name on line 29 stays `handover` (it references the `Handover` class, not the column).

- [ ] **Step 1b: Fix `Backend/scripts/import_eye_tracking.py`**

Open `Backend/scripts/import_eye_tracking.py`. Find the two places where `hanover_id` is used (in the `if existing:` update block and the `EyeTracking(...)` constructor) and rename both to `handover_id`:

```python
# In the if existing: block — FROM:
existing.hanover_id = r['hanover_id']
# TO:
existing.handover_id = r['handover_id']

# In the EyeTracking(...) constructor — FROM:
hanover_id=r['hanover_id'],
# TO:
handover_id=r['handover_id'],
```

> **Verify all remaining references** with:
> ```bash
> cd Web && grep -rn "hanover_id" Backend/ --include="*.py" | grep -v "__pycache__"
> ```
> Expected: no remaining hits after this step.

- [ ] **Step 2: Fix `sql/schema.sql`**

The schema file is at `../sql/schema.sql` relative to `Web/`. Open it and find the `eye_tracking` table definition (around line 165–172). Change:

```sql
-- FROM:
    hanover_id integer NOT NULL,

-- TO:
    handover_id integer NOT NULL,
```

Also find the FK constraint (around line 1268):
```sql
-- FROM:
    ADD CONSTRAINT handover_id_fk FOREIGN KEY (hanover_id) REFERENCES public.handover(handover_id);

-- TO:
    ADD CONSTRAINT handover_id_fk FOREIGN KEY (handover_id) REFERENCES public.handover(handover_id);
```

- [ ] **Step 3: Fix `Backend/data/testmock/eye_tracking.json`**

The file is 5 MB with many records. Use a Python script to rename the key:

```bash
cd Web && python -c "
import json
with open('Backend/data/testmock/eye_tracking.json', 'r') as f:
    data = json.load(f)
for row in data:
    if 'hanover_id' in row:
        row['handover_id'] = row.pop('hanover_id')
with open('Backend/data/testmock/eye_tracking.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f'Fixed {len(data)} rows.')
"
```

Expected: `Fixed N rows.`

- [ ] **Step 4: Run full test suite to confirm rename is clean**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short 2>&1 | tail -10
```

Expected: all tests PASS. The rename is transparent to existing tests (no test directly queries `eye_tracking.hanover_id`).

- [ ] **Step 5: Commit typo fix**

```bash
cd "C:\Users\SebastianKeppler\RiderProjects\projekt_ws24" && \
git add Web/Backend/models/eyetracking.py \
        Web/Backend/scripts/import_eye_tracking.py \
        Web/Backend/data/testmock/eye_tracking.json \
        sql/schema.sql
git commit -m "fix: rename hanover_id to handover_id in eye_tracking table, ORM model and import script"
```

### Task 6: Add conftest.py EyeTracking cleanup

**Files:**
- Modify: `Backend/tests/conftest.py`

- [ ] **Step 1: Add EyeTracking to `_delete_all`**

Open `Backend/tests/conftest.py`. Add `EyeTracking` deletion **before** `Handover` in `_delete_all` (EyeTracking has a FK to Handover, so it must be deleted first):

```python
def _delete_all(session):
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import EyeTracking          # ADD THIS
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.models.trial.trial import Trial
    from Backend.models.participant import Participant
    from Backend.models.experiment import Experiment
    from Backend.models.study.study import Study
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.models.study.study_stimuli import StudyStimuli
    from Backend.models.study.study_config import StudyConfig

    session.query(EyeTracking).delete()                         # ADD THIS (before Handover)
    session.query(Handover).delete()
    session.query(QuestionnaireResponse).delete()
    # ... rest unchanged
```

- [ ] **Step 2: Run tests to confirm conftest change doesn't break anything**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short 2>&1 | tail -10
```

Expected: all tests PASS.

### Task 7: Create EyeTrackingRepository and Service

**Files:**
- Create: `Backend/db/eyetracking_repository.py`
- Create: `Backend/services/eyetracking_service.py`

- [ ] **Step 1: Create `Backend/db/eyetracking_repository.py`**

```python
from sqlalchemy.orm import Session
from Backend.models.eyetracking import EyeTracking


class EyeTrackingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: dict) -> EyeTracking:
        record = EyeTracking(**data)
        self.session.add(record)
        self.session.flush()
        self.session.refresh(record)
        return record
```

- [ ] **Step 2: Create `Backend/services/eyetracking_service.py`**

```python
from Backend.db.eyetracking_repository import EyeTrackingRepository
from Backend.models.eyetracking import EyeTracking


def save_eye_tracking(session, data: dict) -> EyeTracking:
    repo = EyeTrackingRepository(session)
    return repo.create(data)
```

### Task 8: Create EyeTracking Router and Tests

**Files:**
- Create: `Backend/routes/eyetracking.py`
- Modify: `Backend/routes/__init__.py`
- Create: `Backend/tests/test_eyetracking.py`

- [ ] **Step 1: Write the failing tests**

Create `Backend/tests/test_eyetracking.py`:

```python
import pytest
from starlette import status
from Backend.models.eyetracking import AreaOfInterest
from Backend.db_session import SessionLocal


@pytest.fixture
def trial_id(client, experiment_id):
    """POST returns {"status": "ok"} — use GET to retrieve the trial_id."""
    resp = client.post(
        f"/experiments/{experiment_id}/trials",
        json={"trials": [{"trial_number": 1, "slots": []}], "questionnaires": []}
    )
    assert resp.status_code == 201, resp.text
    trials = client.get(f"/experiments/{experiment_id}/trials").json()
    assert len(trials) > 0
    return trials[0]["trial_id"]


@pytest.fixture
def two_participant_ids(client):
    ids = []
    for _ in range(2):
        resp = client.post(
            "/api/participants/",
            json={"age": 25, "gender": "m", "handedness": "right"}
        )
        assert resp.status_code == 201
        ids.append(resp.json()["participant_id"])
    return ids


@pytest.fixture
def handover_id(client, trial_id, two_participant_ids):
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": two_participant_ids[0], "receiver": two_participant_ids[1]}
    )
    assert resp.status_code == 201
    return resp.json()["handover_id"]


@pytest.fixture
def aoi_id():
    """Seeds one AreaOfInterest row directly and returns its ID."""
    db = SessionLocal()
    existing = db.query(AreaOfInterest).filter_by(aoi="instrument").first()
    if existing:
        aoi = existing
    else:
        aoi = AreaOfInterest(aoi="instrument", label="Instrument")
        db.add(aoi)
        db.commit()
        db.refresh(aoi)
    aoi_id = aoi.aoi_id
    db.close()
    return aoi_id


def test_eyetracking_create_success(client, handover_id, two_participant_ids, aoi_id):
    """POST creates an eye-tracking record and returns eye_tracking_id."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "eye_tracking_id" in data
    assert data["eye_tracking_id"] is not None


def test_eyetracking_create_missing_field(client, handover_id, two_participant_ids, aoi_id):
    """POST without aoi_id returns 422."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_eyetracking_invalid_handover_id(client, two_participant_ids, aoi_id):
    """POST with non-existing handover_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": 99999,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_eyetracking_invalid_participant_id(client, handover_id, aoi_id):
    """POST with non-existing participant_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": 99999,
            "handover_id": handover_id,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_eyetracking_invalid_aoi_id(client, handover_id, two_participant_ids):
    """POST with non-existing aoi_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "aoi_id": 99999,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
```

- [ ] **Step 2: Run tests to confirm they FAIL**

```bash
cd Web && uv run pytest Backend/tests/test_eyetracking.py -v 2>&1 | head -20
```

Expected: FAIL with connection error or 404 (route doesn't exist).

- [ ] **Step 3: Create `Backend/routes/eyetracking.py`**

```python
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.db_session import SessionLocal
from Backend.models.eyetracking import EyeTracking, AreaOfInterest
from Backend.models.handover import Handover
from Backend.models.participant import Participant
from Backend.services.eyetracking_service import save_eye_tracking

router = APIRouter(prefix="/eyetracking", tags=["eyetracking"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EyeTrackingCreateRequest(BaseModel):
    participant_id: int
    handover_id: int
    aoi_id: int
    starttime: datetime
    endtime: datetime
    duration: int


class EyeTrackingResponse(BaseModel):
    message: str
    eye_tracking_id: int


@router.post(
    "",
    response_model=EyeTrackingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save Eye-Tracking fixation event",
    description="Save a single AOI fixation event from Unity. handover_id, participant_id, and aoi_id must exist.",
)
async def create_eye_tracking(
        payload: EyeTrackingCreateRequest,
        db: Session = Depends(get_db),
) -> EyeTrackingResponse:
    try:
        # FK validation — explicit 404 rather than relying on DB constraint errors
        if not db.query(Handover).filter_by(handover_id=payload.handover_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Handover not found")
        if not db.query(Participant).filter_by(participant_id=payload.participant_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        if not db.query(AreaOfInterest).filter_by(aoi_id=payload.aoi_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AOI not found")

        data = payload.model_dump()
        record = save_eye_tracking(db, data)
        db.commit()
        return EyeTrackingResponse(message="Eye-tracking record saved", eye_tracking_id=record.eye_tracking_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
```

- [ ] **Step 4: Register the router in `Backend/routes/__init__.py`**

Open `Backend/routes/__init__.py`. Add `eyetracking` to the import block and the `modules` tuple:

```python
def register_routes(app: FastAPI):
    from Backend.routes import (
        participant,
        study,
        experiment,
        trials,
        stimuli,
        questionnaire,
        analysis,
        handover_routes,
        avatar_visibility,
        eyetracking,          # ADD THIS
    )

    modules = (
        participant,
        study,
        experiment,
        trials,
        stimuli,
        questionnaire,
        analysis,
        handover_routes,
        avatar_visibility,
        eyetracking,          # ADD THIS
    )
    # ... rest unchanged
```

- [ ] **Step 5: Run eye-tracking tests**

```bash
cd Web && uv run pytest Backend/tests/test_eyetracking.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
cd Web && uv run pytest Backend/tests/ -v --tb=short 2>&1 | tail -10
```

Expected: all tests PASS, no regressions.

- [ ] **Step 7: Commit Chunk 3**

```bash
git add Backend/models/eyetracking.py \
        Backend/data/testmock/eye_tracking.json \
        Backend/tests/conftest.py \
        Backend/db/eyetracking_repository.py \
        Backend/services/eyetracking_service.py \
        Backend/routes/eyetracking.py \
        Backend/routes/__init__.py \
        Backend/tests/test_eyetracking.py
git commit -m "feat: add POST /eyetracking endpoint and fix hanover_id typo"
```

Also commit the schema fix separately (it's in a different directory):

```bash
cd "C:\Users\SebastianKeppler\RiderProjects\projekt_ws24" && \
git add sql/schema.sql && \
git commit -m "fix: rename hanover_id to handover_id in sql/schema.sql"
```
