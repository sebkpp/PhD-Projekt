from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session

from Backend.db_session import SessionLocal
from Backend.models.trial.trial import TrialCreateRequest
from Backend.services.trial_service import save_trials, get_trials_for_experiment, finish_trial, \
    save_experiment_questionnaires, get_trial, start_trial, get_participants_for_trial

router = APIRouter(prefix="/trials", tags=["trials"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MessageResponse(BaseModel):
    message: str

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None

current_trial_id: Optional[int] = None


@router.post(
    "/experiments/{experiment_id}/trials",
    status_code=status.HTTP_201_CREATED,
    summary="Save trials for an experiment",
    description="Save trial configuration and associated questionnaires for a given experiment."
)
async def save_trials_route(
        experiment_id: int,
        payload: TrialCreateRequest,
        db: Session = Depends(get_db)
):
    try:
        if not payload.trials:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="`trials` is required")
        selected_questionnaires = [q["questionnaire_id"] for q in payload.questionnaires or []]
        result = save_trials(db, experiment_id, payload.trials, selected_questionnaires)
        save_experiment_questionnaires(db, experiment_id, selected_questionnaires)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get(
    "/experiments/{experiment_id}/trials",
    status_code=status.HTTP_200_OK,
    summary="Get trials for an experiment",
    description="Retrieve all trials for a given experiment."
)
async def get_trials_route(
        experiment_id: int,
        db: Session = Depends(get_db)
):
    try:
        trials = get_trials_for_experiment(db, experiment_id)
        return trials
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/trial/{trial_id}/start",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start a trial",
    description="Mark a trial as started."
)
async def start_trial_route(
        trial_id: int,
        db: Session = Depends(get_db)
) -> MessageResponse:
    global current_trial_id
    try:
        start_trial(db, trial_id)
        current_trial_id = trial_id
        db.commit()
        return MessageResponse(message="Trial started")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/trial/{trial_id}/end",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="End a trial",
    description="Mark a trial as finished."
)
async def end_trial_route(
        trial_id: int,
        db: Session = Depends(get_db)
) -> StatusResponse:
    global current_trial_id
    try:
        finish_trial(db, trial_id)
        current_trial_id = None
        db.commit()
        return StatusResponse(status="ok", message=f"Trial {trial_id} marked as finished")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/trial/current_trial",
    status_code=status.HTTP_200_OK,
    summary="Get current trial",
    description="Retrieve the currently active trial ID."
)
async def get_current_trial_route():
    return {"trial_id": current_trial_id}


@router.get(
    "/trial/{trial_id}",
    status_code=status.HTTP_200_OK,
    summary="Get trial by ID",
    description="Retrieve a trial by its ID."
)
async def get_trial_route(
        trial_id: int,
        db: Session = Depends(get_db)
):
    try:
        trial = get_trial(db, trial_id)
        return trial.to_dict()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/trial/{trial_id}/participants",
    status_code=status.HTTP_200_OK,
    summary="Get participants for a trial",
    description="Retrieve all participants for a given trial."
)
async def get_trial_participants_route(
        trial_id: int,
        db: Session = Depends(get_db)
):
    try:
        participants = get_participants_for_trial(db, trial_id)
        return [p.to_dict() for p in participants]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

