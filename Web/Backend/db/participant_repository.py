from typing import List

from sqlalchemy.orm import Session

from ..models import TrialParticipantSlot, Trial, TrialSlot
from ..models.participant import Participant



class ParticipantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_participant(self, age: int, gender: str, handedness: str) -> Participant:
        participant = Participant(age=age, gender=gender, handedness=handedness)
        self.db.add(participant)
        self.db.flush()
        self.db.refresh(participant)
        return participant

    def get_participants_by_experiment(self, experiment_id: int) -> List[Participant]:
        return (
            self.db.query(Participant)
            .join(TrialParticipantSlot, Participant.participant_id == TrialParticipantSlot.participant_id)
            .join(TrialSlot, TrialParticipantSlot.trial_slot_id == TrialSlot.trial_slot_id)
            .join(Trial, TrialSlot.trial_id == Trial.trial_id)
            .filter(Trial.experiment_id == experiment_id)
            .all()
        )