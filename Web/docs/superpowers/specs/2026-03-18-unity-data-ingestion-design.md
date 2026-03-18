# Design-Spec: Unity Data Ingestion API

**Datum:** 2026-03-18
**Branch:** 20-web-interface-for-data-collection
**Status:** Draft v3

---

## 1. Kontext & Ziel

Unity (VR-Anwendung) soll Performance-Daten (Handover-Phasen-Timestamps) und
Eye-Tracking-Daten (AOI-Fixations-Events) in Echtzeit über die FastAPI-Backend-API
in die PostgreSQL-Datenbank schreiben.

Außerdem wird `AvatarVisibility` auf einen einzigen festen Wert reduziert,
da Avatar-Sichtbarkeit kein variierbarer Studienfaktor mehr ist.

---

## 2. AvatarVisibility — Fixed "Full Body"

### 2.1 Entscheidung

Die Tabelle `avatar_visibility` und der FK `trial_slot.avatar_visibility_id` bleiben
unverändert im Schema. Es gibt nur noch einen gültigen Eintrag — der bestehende Eintrag
`"full"` / `"Ganze Figur"` wird beibehalten (keine Umbenennung, kein DB-Migration-Risiko).
Die beiden anderen Einträge (`"hands"`, `"head"`) werden aus der Seed-Datei entfernt.

| avatar_visibility_id | avatar_visibility_name | label        |
|----------------------|------------------------|--------------|
| 1 (auto)             | full                   | Ganze Figur  |

### 2.2 Betroffene Dateien

| Datei | Änderung |
|---|---|
| `Backend/data/static/avatar_visibility.json` | Auf einen Eintrag reduzieren: `[{"name": "full", "label": "Ganze Figur"}]` |
| `Backend/db/trial/trial_slot_repository.py` | `avatar_visibility`-Parameter aus `create()` entfernen; fester Default `avatar_visibility_id=1` |
| `Backend/scripts/import_trial_slot.py` | `avatar_visibility_id` immer auf `1` setzen |
| `Backend/data/testmock/trial_slot.json` | Alle `avatar_visibility_id`-Werte auf `1` setzen (FK-Konsistenz) |
| `Backend/tests/test_avatar_visibility.py` | Fixture auf einzelnen Eintrag `"full"` / `"Ganze Figur"` anpassen (Details: Abschnitt 2.3) |

### 2.3 Test-Anpassungen `test_avatar_visibility.py`

Die Fixture `seeded_avatar_visibility` wird auf einen Eintrag reduziert:
- Nur `AvatarVisibility(avatar_visibility_name="full", label="Ganze Figur")` wird gesetzt

Die drei Tests werden angepasst:
- `test_list_avatar_visibility_empty` — unverändert
- `test_list_avatar_visibility_returns_correct_fields` — `assert len(data) == 1`
- `test_list_avatar_visibility_values` — Assertions aktualisieren:
  - `assert "full" in names` (bleibt)
  - `assert "none" in names` **entfernen**
  - `assert "Ganze Figur" in labels` (war vorher `"Vollständig sichtbar"` — muss geändert werden)
  - `assert "Unsichtbar" in labels` **entfernen**

### 2.4 Kein DB-Schema-Bruch

`sql/schema.sql` wird **nicht** geändert.

---

## 3. Unity Handover API — Handshake-Flow

### 3.1 Überblick

```
Unity                           Backend
  │                                │
  │  POST /handovers/trials/{id}   │
  │  { giver, receiver, object }   │
  │ ─────────────────────────────► │  INSERT Handover (Timestamps NULL)
  │ ◄───────────────────────────── │  → { handover_id }
  │                                │
  │  (Phase tritt ein)             │
  │  PATCH /handovers/{id}/phases  │
  │  { giver_grasped_object: "…" } │
  │ ─────────────────────────────► │  UPDATE einzelne Timestamp-Felder
  │ ◄───────────────────────────── │  → 200 OK
  │                                │
  │  (weitere Phasen …)            │
  │  PATCH /handovers/{id}/phases  │
  │  { receiver_grasped_object,    │
  │    giver_released_object }     │
  │ ─────────────────────────────► │
  │                                │
  │  (Fehler aufgetreten)          │
  │  PATCH /handovers/{id}/phases  │
  │  { is_error: true,             │
  │    error_type: "drop" }        │
  │ ─────────────────────────────► │
```

### 3.2 POST /handovers/trials/{trial_id} — Reparatur

Der Endpoint existiert bereits, hat aber Probleme im Request-Schema.

**Aktuell (fehlerhaft):** Timing-Felder als `Optional[str]` im Init-Request —
sie gehören nicht in den Init-Request (kommen via PATCH).

Folgende vier Felder werden aus `HandoverCreateRequest` **entfernt**:
- `giver_grasped_object: Optional[str]`
- `receiver_touched_object: Optional[str]`
- `receiver_grasped_object: Optional[str]`
- `giver_released_object: Optional[str]`

**Neu (korrigiert):**

```python
class HandoverCreateRequest(BaseModel):
    giver: int
    receiver: int
    grasped_object: Optional[str] = None
```

**Hinweis `create_handover` in HandoverRepository:** Die Methode `create_handover`
(Zeilen 48–62 in `handover_repository.py`) iteriert über diese vier Keys und ruft
`parse_iso()` für sie auf. Da sie nach der Änderung nie mehr im `handover_data`-Dict
vorhanden sein werden, ist diese Logik toter Code — sie schadet nicht, kann aber
zusammen mit der Änderung bereinigt werden (die `parse_iso`-Schleife über die vier
Timestamp-Keys entfernen oder die Methode auf Pydantic-Typen umstellen).

**Response** (unverändert):
```python
class MessageResponse(BaseModel):
    message: str
    handover_id: Optional[int] = None
```

### 3.3 PATCH /handovers/{handover_id}/phases — Neu

**Route:** `PATCH /handovers/{handover_id}/phases`
**Status:** 200 OK

**Request-Schema:**

```python
class HandoverPhasePatchRequest(BaseModel):
    giver_grasped_object: Optional[datetime] = None
    receiver_touched_object: Optional[datetime] = None
    receiver_grasped_object: Optional[datetime] = None
    giver_released_object: Optional[datetime] = None
    is_error: Optional[bool] = None
    error_type: Optional[str] = None
```

**Partial-Update-Semantik:** Felder die `None` sind oder weggelassen werden, werden
**nicht** überschrieben — nur explizit gesetzte Felder werden in der DB aktualisiert.
**Einschränkung:** Ein Timestamp kann über PATCH nicht nachträglich auf NULL zurückgesetzt
werden. Diese Funktion ist bewusst nicht vorgesehen.

**Route Handler:** Konvertiert `HandoverPhasePatchRequest` mit `payload.model_dump()`
(ohne `exclude_none=True`) zu einem Dict — die Repository-Methode filtert `None`-Werte
selbst heraus. Ruft dann `update_handover_phases`, dann **`db.commit()`** (wie
`save_handover_route`), dann 200 zurück. Fehlerfall: 404 wenn `handover_id` nicht
existiert (Service gibt `None` zurück).

**Response:**
```python
class MessageResponse(BaseModel):
    message: str
    handover_id: Optional[int] = None
```

### 3.4 Neue Repository-Methode

In `Backend/db/handover_repository.py` neue Methode `update_handover_phases`:

```python
def update_handover_phases(self, handover_id: int, patch_data: dict) -> Optional[Handover]:
    handover = self.session.query(Handover).filter_by(handover_id=handover_id).first()
    if handover is None:
        return None
    updatable = [
        "giver_grasped_object", "receiver_touched_object",
        "receiver_grasped_object", "giver_released_object",
        "is_error", "error_type"
    ]
    for field in updatable:
        if field in patch_data and patch_data[field] is not None:
            setattr(handover, field, patch_data[field])
    self.session.flush()
    return handover
```

### 3.5 Neue Service-Funktion

In `Backend/services/handover_service.py` ergänzen:

```python
def update_handover_phases(session, handover_id: int, patch_data: dict):
    repo = HandoverRepository(session)
    return repo.update_handover_phases(handover_id, patch_data)
```

---

## 4. Eye-Tracking API — Neu

### 4.1 Tippfehler-Fix: hanover_id → handover_id

**Implementierungsreihenfolge:** Die ORM-Umbenennung (`models/eyetracking.py`) und die
SQL-Schema-Anpassung (`sql/schema.sql`) müssen **vor** der Implementierung des
`EyeTrackingRepository` und des Routes-Handlers abgeschlossen sein, da der Repository-Code
den korrekten Spaltennamen `handover_id` voraussetzt.

**Betroffene Dateien:**

| Datei | Änderung |
|---|---|
| `Backend/models/eyetracking.py` | `hanover_id` → `handover_id` (Spaltenname + FK-Attribut) |
| `sql/schema.sql` | Spaltenname `hanover_id` → `handover_id` in `eye_tracking`-Tabelle |
| `Backend/data/testmock/eye_tracking.json` | `"hanover_id"` → `"handover_id"` in allen Einträgen |

### 4.2 POST /eyetracking — Neuer Endpoint

**Route:** `POST /eyetracking`
**Status:** 201 Created

**Request-Schema:**
```python
class EyeTrackingCreateRequest(BaseModel):
    participant_id: int
    handover_id: int
    aoi_id: int
    starttime: datetime
    endtime: datetime
    duration: int  # Millisekunden
```

**FK-Validierung vor dem DB-Insert:**
- `handover_id`: 404 wenn nicht in `handover`-Tabelle
- `participant_id`: 404 wenn nicht in `participant`-Tabelle
- `aoi_id`: 404 wenn nicht in `area_of_interest`-Tabelle
  (alle drei müssen explizit im Route-Handler geprüft werden, bevor der Insert erfolgt —
  DB-Constraint-Fehler werden als 500 weitergegeben, nicht als 404)

**Response:**
```python
class EyeTrackingResponse(BaseModel):
    message: str
    eye_tracking_id: int
```

Route Handler ruft `save_eye_tracking`, dann **`db.commit()`**, dann 201 zurück.

### 4.3 Neue Datei: EyeTrackingRepository

`Backend/db/eyetracking_repository.py`:

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

### 4.4 Neue Datei: EyeTracking Service

`Backend/services/eyetracking_service.py`:

```python
from Backend.db.eyetracking_repository import EyeTrackingRepository
from Backend.models.eyetracking import EyeTracking

def save_eye_tracking(session, data: dict) -> EyeTracking:
    repo = EyeTrackingRepository(session)
    return repo.create(data)
```

### 4.5 Neue Datei: EyeTracking Router

`Backend/routes/eyetracking.py` — neuer Router mit Prefix `/eyetracking`.

**Registrierung:** `Backend/routes/__init__.py` muss manuell angepasst werden —
`eyetracking` zum Import-Block und zur `modules`-Tuple hinzufügen (statisches
Import-Pattern, nicht automatisch).

---

## 5. Tests

### 5.1 Handover-Tests (neue Datei `Backend/tests/test_handover.py`)

| Test | Beschreibung |
|---|---|
| `test_handover_init_creates_record` | POST → 201, `handover_id` in Response |
| `test_handover_init_missing_giver` | POST ohne `giver` → 422 |
| `test_handover_patch_phases_updates_timestamps` | PATCH → 200, Timestamps in DB gesetzt |
| `test_handover_patch_partial_update` | PATCH mit einem Feld → andere Felder bleiben NULL |
| `test_handover_patch_not_found` | PATCH auf nicht existierende ID → 404 |
| `test_handover_patch_sets_is_error` | PATCH mit `is_error=True`, `error_type` → korrekt gespeichert |

### 5.2 Eye-Tracking-Tests (neue Datei `Backend/tests/test_eyetracking.py`)

| Test | Beschreibung |
|---|---|
| `test_eyetracking_create_success` | POST → 201, `eye_tracking_id` in Response |
| `test_eyetracking_create_missing_field` | POST ohne `aoi_id` → 422 |
| `test_eyetracking_invalid_handover_id` | POST mit nicht existierender `handover_id` → 404 |
| `test_eyetracking_invalid_aoi_id` | POST mit nicht existierender `aoi_id` → 404 |
| `test_eyetracking_invalid_participant_id` | POST mit nicht existierender `participant_id` → 404 |

---

## 6. Nicht in diesem Spec

- **Unity-seitige Implementierung** der API-Calls (separates Unity-Thema)
- **Auth/API-Key** für Unity-Endpoints (zukünftiger Spec)
- **Batch-Endpoint** für ET-Daten (bewusst nicht gewählt, Real-time bevorzugt)

---

## 7. Dateienübersicht

| Datei | Aktion |
|---|---|
| `Backend/data/static/avatar_visibility.json` | Ändern — auf 1 Eintrag `"full"` reduzieren |
| `Backend/db/trial/trial_slot_repository.py` | Ändern — fester Default `avatar_visibility_id=1` |
| `Backend/scripts/import_trial_slot.py` | Ändern — `avatar_visibility_id=1` hardcoded |
| `Backend/data/testmock/trial_slot.json` | Ändern — alle `avatar_visibility_id` auf `1` setzen |
| `Backend/tests/test_avatar_visibility.py` | Ändern — Fixture auf `"full"` anpassen, Counts auf 1 |
| `Backend/models/eyetracking.py` | Ändern — `hanover_id` → `handover_id` |
| `sql/schema.sql` | Ändern — `hanover_id` → `handover_id` in `eye_tracking` |
| `Backend/data/testmock/eye_tracking.json` | Ändern — `"hanover_id"` → `"handover_id"` |
| `Backend/routes/handover_routes.py` | Ändern — `HandoverCreateRequest` bereinigen, PATCH-Endpoint hinzufügen |
| `Backend/db/handover_repository.py` | Ändern — `update_handover_phases` hinzufügen |
| `Backend/services/handover_service.py` | Ändern — `update_handover_phases` hinzufügen |
| `Backend/routes/__init__.py` | Ändern — `eyetracking` zum Import-Block und `modules`-Tuple hinzufügen |
| `Backend/db/eyetracking_repository.py` | Neu — `EyeTrackingRepository` |
| `Backend/services/eyetracking_service.py` | Neu — `save_eye_tracking` |
| `Backend/routes/eyetracking.py` | Neu — `POST /eyetracking` Router |
| `Backend/tests/test_handover.py` | Neu — Handover-Tests |
| `Backend/tests/test_eyetracking.py` | Neu — Eye-Tracking-Tests |
| `Backend/tests/conftest.py` | Ändern — `_delete_all` um `EyeTracking`-Löschung ergänzen (vor `Handover`, da FK) |
