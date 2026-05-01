# Database Schema

PostgreSQL 17. Source of truth: `schema.sql`. The SQLAlchemy ORM models in `Web/Backend/models/` mirror this schema.

## Tables

### Study & Experiment Structure

| Table | Description |
|---|---|
| `study` | Top-level container for a research study. Tracks status (`created`, `active`, `Beendet`) and dates. |
| `study_config` | Configuration attached to a study: name, principal investigator, number of trials, randomisation flag, study type. |
| `experiment` | A single run of a study with a specific group of participants. Belongs to a `study`. |
| `trial` | One task block within an experiment. Belongs to an `experiment`. Tracks completion status. |
| `trial_slot` | A role slot within a trial (e.g. giver / receiver). Carries the assigned `avatar_visibility`. |
| `trial_slot_stimulus` | Which stimuli are active for a given `trial_slot`. Junction table. |
| `trial_participant_slot` | Maps a `participant` to a `trial_slot`. Junction table. |

### Participants

| Table | Description |
|---|---|
| `participant` | A study participant. Stores demographic data (age, gender, handedness). |

### Handover & Eye Tracking

| Table | Description |
|---|---|
| `handover` | A single object handover event within a trial. Records precise timestamps for each phase (giver grasped, giver released, receiver touched, receiver grasped) and the object involved. Also stores error flags. |
| `eye_tracking` | A single area-of-interest (AOI) fixation event recorded during a handover. Linked to a `handover`, `participant`, and `area_of_interest`. Stores start time, end time, and duration in ms. |

### Stimuli

| Table | Description |
|---|---|
| `stimulus_type` | Category of a stimulus (e.g. `visual`, `auditory`, `tactile`). Seed data. |
| `stimuli` | A concrete stimulus instance, belonging to a `stimulus_type`. Has a name and description. |
| `stimulus_visual` | Visual-specific properties for a stimulus (display name). |
| `stimulus_auditiv` | Auditory-specific properties (frequency in Hz, volume). |
| `stimulus_tactile` | Tactile-specific properties (vibration pattern, intensity). |
| `stimuli_combination` | A named combination of multiple stimuli, stored as a text key. |
| `stimulus_combination_item` | Junction table linking `stimuli` to a `stimuli_combination`. |
| `study_stimuli` | Which stimulus types are active for a given study. Junction table. |

### Questionnaires

| Table | Description |
|---|---|
| `questionnaire` | A questionnaire definition with a name and scale configuration (type, min, max). |
| `questionnaire_item` | A single item (question) within a `questionnaire`. Stores label, description, and scale endpoint labels. |
| `questionnaire_response` | A participant's response to a single `questionnaire_item` in a specific trial. |
| `study_questionnaire` | Which questionnaires are assigned to a study, with ordering and trigger timing. |
| `experiment_questionnaire` | Which questionnaires are assigned to a specific experiment. |

### Reference / Seed Data

| Table | Description |
|---|---|
| `area_of_interest` | Named regions of the virtual scene used for eye tracking analysis (e.g. `hand`, `object`). Seed data. |
| `avatar_visibility` | Visibility configurations for participant avatars within a trial slot (e.g. full body, hands only, invisible). Seed data. |

## Schema Changes

Any schema change must be reflected in:
1. `sql/schema.sql`
2. The corresponding ORM model in `Web/Backend/models/`
3. Unity API compatibility (if the changed table is read/written by the Unity application)
