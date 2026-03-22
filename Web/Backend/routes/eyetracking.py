from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.db_session import SessionLocal
from Backend.models.eyetracking import EyeTracking, AreaOfInterest
from Backend.models.handover import Handover
from Backend.models.participant import Participant
from Backend.services.eyetracking_service import save_eye_tracking

router = APIRouter(prefix="/eyetracking", tags=["eyetracking"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EyeTrackingCreateRequest(BaseModel):
    participant_id: int
    handover_id: int
    aoi_id: int
    starttime: datetime
    endtime: datetime
    duration: int


class EyeTrackingResponse(BaseModel):
    message: str
    eye_tracking_id: int


@router.post(
    "",
    response_model=EyeTrackingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save Eye-Tracking fixation event",
    description="Save a single AOI fixation event from Unity. handover_id, participant_id, and aoi_id must exist.",
)
async def create_eye_tracking(
        payload: EyeTrackingCreateRequest,
        db: Session = Depends(get_db),
) -> EyeTrackingResponse:
    try:
        # FK validation — explicit 404 rather than relying on DB constraint errors
        if not db.query(Handover).filter_by(handover_id=payload.handover_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Handover not found")
        if not db.query(Participant).filter_by(participant_id=payload.participant_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        if not db.query(AreaOfInterest).filter_by(aoi_id=payload.aoi_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AOI not found")

        data = payload.model_dump()
        record = save_eye_tracking(db, data)
        db.commit()
        return EyeTrackingResponse(message="Eye-tracking record saved", eye_tracking_id=record.eye_tracking_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
