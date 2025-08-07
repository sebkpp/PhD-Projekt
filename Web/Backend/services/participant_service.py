from sqlalchemy.orm import Session
from ..db.participant_repository import create_participant
from ..models.participant import Participant
from .participant_submission_service import (
    submit_participant_to_slot as internal_submit,
    get_submission_status as internal_get_status
)


def register_participant(db: Session, age: int, gender: str, handedness: str) -> Participant:
    """
    Erstellt einen neuen Teilnehmer in der Datenbank.
    """
    return create_participant(db, age, gender, handedness)


def submit_participant_to_slot(experiment_id: int, slot: int, participant_id: int):
    """
    Markiert einen Slot in einem Experiment als 'submitted' mit zugehöriger participant_id.
    """
    if not all([experiment_id, slot, participant_id]):
        raise ValueError("experiment_id, slot oder participant_id fehlt")

    internal_submit(experiment_id, slot, participant_id)


def get_submission_status(experiment_id: int, slot: int) -> dict:
    """
    Gibt zurück, ob ein bestimmter Slot in einem Experiment bereits als 'submitted' markiert ist.
    """
    if not experiment_id or slot is None:
        raise ValueError("experiment_id oder slot fehlt")

    return internal_get_status(experiment_id, slot)
