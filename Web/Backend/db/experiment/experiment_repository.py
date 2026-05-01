from typing import Type
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from Backend.models.experiment import Experiment

class ExperimentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, study_id:int, description : str, researcher: str) -> Experiment:
        experiment = Experiment(
            description=description,
            researcher=researcher,
            study_id=study_id
        )
        self.session.add(experiment)
        self.session.flush()
        return experiment

    def get_by_id(self, experiment_id: int) -> Experiment | None:
        return self.session.query(Experiment).filter_by(experiment_id=experiment_id).first()

    def get_by_study(self, study_id: int) -> list[Type[Experiment]]:
        return self.session.query(Experiment).filter_by(study_id=study_id).all()

    def set_started_at(self, experiment: Experiment):
        experiment.started_at = datetime.now(timezone.utc)
        self.session.commit()

    def set_completed_at(self, experiment: Experiment):
        experiment.completed_at = datetime.now(timezone.utc)
        self.session.commit()
