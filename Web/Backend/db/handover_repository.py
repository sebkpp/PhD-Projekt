from datetime import datetime

from sqlalchemy.orm import Session

from Backend.models import Trial
from Backend.models.experiment import Experiment
from Backend.models.handover import Handover

def parse_iso(dt_str):
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


class HandoverRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_handovers_for_trial(self, trial_id: int):
        return (
            self.session.query(Handover)
            .filter(Handover.trial_id == trial_id)
            .order_by(Handover.handover_id)
            .all()
        )

    def get_handovers_by_experiment(self, experiment_id: int):
        return (
            self.session.query(Handover)
            .join(Trial, Handover.trial_id == Trial.trial_id)
            .filter(Trial.experiment_id == experiment_id)
            .order_by(Handover.handover_id)
            .all()
        )

    def get_handovers_by_study(self, study_id: int):
        """Gibt alle Handovers einer Studie zurück (über Trial → Experiment → Study)."""
        return (
            self.session.query(Handover)
            .join(Trial, Handover.trial_id == Trial.trial_id)
            .join(Experiment, Trial.experiment_id == Experiment.experiment_id)
            .filter(Experiment.study_id == study_id)
            .order_by(Handover.handover_id)
            .all()
        )


    def create_handover(self, handover_data: dict) -> Handover:
        handover = Handover(**handover_data)
        self.session.add(handover)
        self.session.flush()
        self.session.refresh(handover)
        return handover

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