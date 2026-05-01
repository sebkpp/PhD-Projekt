from sqlalchemy.orm import Session
from Backend.models.eyetracking import EyeTracking


class EyeTrackingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: dict) -> EyeTracking:
        record = EyeTracking(**data)
        self.session.add(record)
        self.session.flush()
        self.session.refresh(record)
        return record
