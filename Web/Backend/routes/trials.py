from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Backend.db_session import SessionLocal
from Backend.models.participant import ParticipantResponse
from Backend.models.trial.trial import TrialResponse
from Backend.services.trial_service import finish_trial, \
    get_trial, start_trial, get_participants_for_trial, get_stimuli_for_trial

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


class CurrentTrialResponse(BaseModel):
    trial_id: Optional[int] = None


current_trial_id: Optional[int] = None



@router.post(
    "/{trial_id}/start",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Start a trial",
    description="Mark a trial as started.",
    responses={
        404: {"description": "Trial not found"},
        500: {"description": "Internal server error"},
    },
)
async def start_trial_route(
        trial_id: int = Path(description="The ID of the trial to start"),
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
    "/{trial_id}/end",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="End a trial",
    description="Mark a trial as finished.",
    responses={
        404: {"description": "Trial not found"},
        500: {"description": "Internal server error"},
    },
)
async def end_trial_route(
        trial_id: int = Path(description="The ID of the trial to end"),
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/current",
    response_model=CurrentTrialResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current trial",
    description="Retrieve the currently active trial ID.",
)
async def get_current_trial_route() -> CurrentTrialResponse:
    return CurrentTrialResponse(trial_id=current_trial_id)


@router.get(
    "/{trial_id}",
    response_model=TrialResponse,
    status_code=status.HTTP_200_OK,
    summary="Get trial by ID",
    description="Retrieve a trial by its ID.",
    responses={
        404: {"description": "Trial not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_trial_route(
        trial_id: int = Path(description="The ID of the trial to retrieve"),
        db: Session = Depends(get_db)
) -> TrialResponse:
    try:
        trial = get_trial(db, trial_id)
        if trial is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trial not found")
        return TrialResponse(**trial.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{trial_id}/participants",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Get participants for a trial",
    description="Retrieve all participants for a given trial.",
    responses={
        404: {"description": "Trial not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_trial_participants_route(
        trial_id: int = Path(description="The ID of the trial whose participants to retrieve"),
        db: Session = Depends(get_db)
) -> List[ParticipantResponse]:
    try:
        participants = get_participants_for_trial(db, trial_id)
        return [p.to_dict() for p in participants]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{trial_id}/stimuli",
    status_code=status.HTTP_200_OK,
    summary="Get stimuli for a trial",
    description="Returns all slot stimuli configurations for the given trial."
)
async def get_trial_stimuli_route(
        trial_id: int,
        db: Session = Depends(get_db)
):
    try:
        return get_stimuli_for_trial(db, trial_id)
    except ValueError as e:
        if str(e) == "trial_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trial not found")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

