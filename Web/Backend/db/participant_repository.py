from sqlalchemy.orm import Session
from ..models.participant import Participant


def create_participant(db: Session, age: int, gender: str, handedness: str) -> Participant:
    participant = Participant(age=age, gender=gender, handedness=handedness)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant
