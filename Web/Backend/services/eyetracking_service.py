from Backend.db.eyetracking_repository import EyeTrackingRepository
from Backend.models.eyetracking import EyeTracking


def save_eye_tracking(session, data: dict) -> EyeTracking:
    repo = EyeTrackingRepository(session)
    return repo.create(data)
