from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from Backend.db_session import SessionLocal
from Backend.services.experiment_service import get_experiment_by_id
from Backend.services.handover_service import save_handover, get_handovers_for_trial, get_handovers_for_experiment
from Backend.services.trial_service import get_trial

router = APIRouter(prefix="/handovers", tags=["handovers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class HandoverResponse(BaseModel):
    handover_id: int
    trial_id: int
    giver: int
    receiver: int
    timestamp: Optional[str] = None
    # weitere Felder nach Bedarf

    class Config:
        orm_mode = True

class HandoverCreateRequest(BaseModel):
    giver: int
    receiver: int
    grasped_object: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    handover_id: Optional[int] = None

@router.get(
    "/trials/{trial_id}",
    response_model=List[HandoverResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Handovers for Trial",
    description="Retrieve all handovers associated with a specific trial."
)
async def get_handovers_for_trial_route(
        trial_id: int,
        db: Session = Depends(get_db)
) -> List[HandoverResponse]:
    try:
        trial = get_trial(db, trial_id)
        if trial is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trial not found")
        handovers = get_handovers_for_trial(db, trial_id)
        return handovers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiments/{experiment_id}",
    response_model=List[HandoverResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Handovers for Experiment",
    description="Retrieve all handovers associated with a specific experiment."
)
async def get_handovers_for_experiment_route(
        experiment_id: int,
        db: Session = Depends(get_db)
) -> List[HandoverResponse]:
    try:
        experiment = get_experiment_by_id(db, experiment_id)
        if experiment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
        handovers = get_handovers_for_experiment(db, experiment_id)
        return handovers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/trials/{trial_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save Handover for Trial",
    description="Save a new handover associated with a specific trial."
)
async def save_handover_route(
        trial_id: int,
        payload: HandoverCreateRequest,
        db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        data = payload.model_dump()
        data["trial_id"] = trial_id
        new_handover = save_handover(db, data)
        db.commit()
        return MessageResponse(message="Handover saved", handover_id=new_handover.handover_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))