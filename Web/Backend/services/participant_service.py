from sqlalchemy.orm import Session

from ..db.participant_repository import ParticipantRepository
from ..db.trial.trial import TrialRepository
from ..db.trial.trial_participant_slot import TrialParticipantSlotRepository
from ..db.trial.trial_slot_repository import TrialSlotRepository
from ..models.participant import Participant
from .participant_submission_service import (
    submit_participant_to_slot as internal_submit,
)


def register_participant(session: Session, age: int, gender: str, handedness: str) -> Participant:
    p_repo = ParticipantRepository(session)
    return p_repo.create_participant( age, gender, handedness)


def submit_participant_to_slot(session, experiment_id: int, slot: int, participant_id: int):

    if not all([experiment_id, slot, participant_id]):
        raise ValueError("experiment_id, slot oder participant_id fehlt")

    t_repo = TrialRepository(session)
    trials = t_repo.get_by_experiment_id(experiment_id)

    ts_repo = TrialSlotRepository(session)
    tps_repo = TrialParticipantSlotRepository(session)

    for trial in trials:
        trial_slots = ts_repo.get_by_trial_id(trial.trial_id, slot)
        for trial_slot in trial_slots:
            tps_repo.create(
                trial_slot_id=trial_slot.trial_slot_id,
                participant_id=participant_id
            )

    #internal_submit(experiment_id, slot, participant_id)

def get_submission_status(session, experiment_id: int, slot: int):
    t_repo = TrialRepository(session)
    ts_repo = TrialSlotRepository(session)
    tps_repo = TrialParticipantSlotRepository(session)

    result = {}
    trials = t_repo.get_by_experiment_id(experiment_id)
    for trial in trials:
        trial_slots = ts_repo.get_by_trial_id(trial.trial_id, slot)
        for trial_slot in trial_slots:
            slot_entries = tps_repo.get_by_slot_id(trial_slot.trial_slot_id)
            for entry in slot_entries:
                if entry.participant_id:
                    result[entry.participant_id] = True
                else:
                    result[entry.participant_id] = False
    return result

def get_participants_by_experiment(session: Session, experiment_id: int):
    p_repo = ParticipantRepository(session)
    participants = p_repo.get_participants_by_experiment(experiment_id)
    print("Participants for experiment", experiment_id, ":", participants)
    return participants