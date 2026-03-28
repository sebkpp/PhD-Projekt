from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from Backend.models.trial.trial import TrialCreateRequest
from Backend.services.experiment_service import create_experiment, get_experiment_by_id, \
    save_experiment_questionnaires, set_experiment_started_at, set_experiment_completed_at, \
    get_next_open_experiment
from Backend.db_session import SessionLocal
from Backend.services.trial_service import save_trials, get_trials_for_experiment

router = APIRouter(prefix="/experiments", tags=["experiments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExperimentCreateRequest(BaseModel):
    name: str
    study_id: int
    description: Optional[str] = None
    researcher: Optional[str] = None

class ExperimentResponse(BaseModel):
    experiment_id: int
    description: Optional[str] = None
    researcher: Optional[str] = None
    study_id: Optional[int] = None

    class Config:
        from_attributes = True

class ExperimentIdResponse(BaseModel):
    experiment_id: int

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str


@router.post(
    "/",
    response_model=ExperimentIdResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Experiment",
    description="Create a new experiment in the system."
)
async def create_experiment_route(
        payload: ExperimentCreateRequest,
        db: Session = Depends(get_db)
) -> ExperimentIdResponse:
    try:
        data = {"experimentSettings": payload.model_dump()}
        experiment = create_experiment(db, data)
        db.commit()
        return ExperimentIdResponse(experiment_id=experiment.experiment_id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")



class NextExperimentResponse(BaseModel):
    experiment_id: int
    trial_id: int
    slots: list[dict]


@router.get(
    "/next",
    response_model=NextExperimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get next open experiment",
    description="Returns the oldest open experiment with its next unfinished trial and slot gender data."
)
async def get_next_experiment_route(db: Session = Depends(get_db)) -> NextExperimentResponse:
    try:
        result = get_next_open_experiment(db)
        return result
    except ValueError as e:
        code = str(e)
        if code in ("no_open_experiment", "no_unfinished_trial"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=code)
        if code == "slots_not_assigned":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=code)


@router.get(
    "/{experiment_id}",
    response_model=ExperimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Experiment by ID",
    description="Retrieve an experiment by its ID."
)
async def get_experiment_route(
        experiment_id: int,
        db: Session = Depends(get_db)
) -> ExperimentResponse:
    try:
        experiment = get_experiment_by_id(db, experiment_id)
        if not experiment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
        return experiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put(
    "/{experiment_id}/questionnaires",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Linked Questionnaires",
    description="Update the questionnaires linked to a specific experiment."
)
async def update_linked_questionnaires(
        experiment_id: int,
        questionnaire_ids: List[int],
        db: Session = Depends(get_db)
) -> MessageResponse:
    experiment = get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    try:
        save_experiment_questionnaires(db, experiment_id, questionnaire_ids)
        db.commit()
        return MessageResponse(message="Questionnaires updated")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/{experiment_id}/started",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Set Experiment Started",
    description="Set the started_at timestamp for a specific experiment."
)
async def set_experiment_started(
        experiment_id: int,
        db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        set_experiment_started_at(db, experiment_id)
        db.commit()
        return MessageResponse(message="Experiment started_at set")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/{experiment_id}/completed",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Set Experiment Completed",
    description="Set the completed_at timestamp for a specific experiment."
)
async def set_experiment_completed(
        experiment_id: int,
        db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        set_experiment_completed_at(db, experiment_id)
        db.commit()
        return MessageResponse(message="Experiment completed_at set")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/{experiment_id}/trials",
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
    "/{experiment_id}/trials",
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
