from datetime import datetime, timezone
from typing import Type

from sqlalchemy.orm import Session
from Backend.models.study.study import Study
class StudyRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: dict) -> Study:
        study = Study(
            status=data.get("status"),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at")
        )
        self.session.add(study)
        self.session.flush()
        return study

    def get_by_id(self, study_id: int) -> Study | None:
        return self.session.query(Study).filter_by(study_id=study_id).first()

    def get_all(self) -> list[Type[Study]]:
        return self.session.query(Study).all()

    def delete(self, study_id: int) -> int:
        return self.session.query(Study).filter_by(study_id=study_id).delete()

    def update(self, study: Study, data: dict) -> Study:
        for key, value in data.items():
            if key == "config" and study.config and isinstance(value, dict):
                for c_key, c_value in value.items():
                    setattr(study.config, c_key, c_value)
            elif key == "stimuli" and isinstance(value, list):
                study.stimuli.clear()
                for stim in value:
                    study.stimuli.append(stim)
            elif key == "questionnaires" and isinstance(value, list):
                study.study_questionnaires.clear()
                for q in value:
                    study.study_questionnaires.append(q)
            elif not isinstance(value, list) and key not in ["config", "stimuli", "questionnaires"]:
                setattr(study, key, value)
        return study

    def set_started_at(self, study, started_at=None):
        study.started_at = started_at or datetime.now(timezone.utc)
        study.status = "Aktiv"
        self.session.flush()
        return study

    def set_ended_at(self, study, ended_at=None):
        study.ended_at = ended_at or datetime.now(timezone.utc)
        study.status = "Beendet"
        self.session.flush()
        return study