from sqlalchemy.orm import Session
from Backend.models.study.study_config import StudyConfig

def create_study_config(session: Session, study_id:int, data: dict) -> StudyConfig:
    config = StudyConfig(
        name=data.get("name"),
        description=data.get("description"),
        principal_investigator=data.get("principal_investigator"),
        study_id=study_id,
        trial_number=data.get("trial_number"),
        trials_permuted=data.get("trials_permuted")
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

def get_study_config_by_id(session: Session, config_id: int) -> StudyConfig | None:
    return session.query(StudyConfig).filter_by(study_config_id=config_id).first()

def get_study_config_by_study_id(session: Session, study_id: int) -> StudyConfig | None:
    return session.query(StudyConfig).filter_by(study_id=study_id).first()

def update_study_config(session: Session, config_id: int, data: dict) -> StudyConfig | None:
    config = get_study_config_by_id(session, config_id)
    if not config:
        return None
    for key, value in data.items():
        setattr(config, key, value)
    return config

def delete_study_config(session: Session, config_id: int) -> int:
    return session.query(StudyConfig).filter_by(study_config_id=config_id).delete()