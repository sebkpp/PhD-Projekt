from sqlalchemy.orm import Session
from Backend.models.study.study_stimuli import StudyStimuli
from Backend.models.stimulus import StimulusType

STIMULI_TYPE_MAP = {
    "vis": "visual",
    "aud": "auditory",
    "tak": "tactile",
    # weitere Mappings
}

def create_study_stimuli(session: Session, study_id: int, stimuli_type_id: int) -> StudyStimuli:
    entry = StudyStimuli(study_id=study_id, stimuli_type_id=stimuli_type_id)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

def get_study_stimuli(session: Session, study_id: int = None) -> list[StudyStimuli]:
    query = session.query(StudyStimuli)
    if study_id is not None:
        query = query.filter_by(study_id=study_id)
    return query.all()

def get_study_stimuli_by_ids(session: Session, study_id: int, stimuli_type_id: int) -> StudyStimuli | None:
    return session.query(StudyStimuli).filter_by(study_id=study_id, stimuli_type_id=stimuli_type_id).first()

def get_stimuli_type_id_by_name(session, name):
    db_name = STIMULI_TYPE_MAP.get(name, name)
    entry = session.query(StimulusType).filter_by(type_name=db_name).first()
    return entry.stimulus_type_id if entry else None

def delete_study_stimuli(session: Session, study_id: int, stimuli_type_id: int) -> int:
    query = session.query(StudyStimuli).filter_by(study_id=study_id)
    if stimuli_type_id is not None:
        query = query.filter_by(stimuli_type_id=stimuli_type_id)
    return query.delete()
def study_stimulus_exists(session, study_id, stimuli_type_id):
    return session.query(StudyStimuli).filter_by(
        study_id=study_id,
        stimuli_type_id=stimuli_type_id
    ).first() is not None