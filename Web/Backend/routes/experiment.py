import traceback
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Path
from pydantic import BaseModel

from sqlalchemy.orm import Session

from Backend.models.experiment import ExperimentResponse
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

class ExperimentSettingsCreate(BaseModel):
    description: Optional[str] = None
    study_id: int
    researcher: Optional[str] = None
    trialConfig: Optional[Any] = None

class ExperimentCreateRequest(BaseModel):
    experimentSettings: ExperimentSettingsCreate

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
        data = payload.model_dump()
        experiment = create_experiment(db, data)
        db.flush()

        trial_config = payload.experimentSettings.trialConfig or {}
        if trial_config:
            trials_list = [
                {
                    "trial_number": int(trial_key.replace("Trial ", "")),
                    "slots": slot_configs
                }
                for trial_key, slot_configs in trial_config.items()
            ]
            save_trials(db, experiment.experiment_id, trials_list, [])

        db.commit()
        return ExperimentIdResponse(experiment_id=experiment.experiment_id)
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



class TrialSlotParticipant(BaseModel):
    slot: int
    gender: str
    participant_id: int
    stimuli: list[Any] = []

class NextExperimentResponse(BaseModel):
    experiment_id: int
    trial_id: int
    slots: list[TrialSlotParticipant]


@router.get(
    "/next",
    response_model=NextExperimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get next open experiment",
    description="Returns the oldest open experiment with its next unfinished trial and slot gender data.",
    responses={
        404: {"description": "No open experiment or unfinished trial"},
        409: {"description": "Slots not assigned"},
        500: {"description": "Internal server error"},
    }
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
    description="Retrieve an experiment by its ID.",
    responses={
        404: {"description": "Experiment not found"},
        500: {"description": "Internal server error"},
    }
)
async def get_experiment_route(
        experiment_id: int = Path(..., description="Numeric ID of the experiment"),
        db: Session = Depends(get_db)
) -> ExperimentResponse:
    try:
        experiment = get_experiment_by_id(db, experiment_id)
        if not experiment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
        return experiment.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put(
    "/{experiment_id}/questionnaires",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Linked Questionnaires",
    description="Update the questionnaires linked to a specific experiment.",
    responses={
        404: {"description": "Experiment not found"},
        500: {"description": "Internal server error"},
    }
)
async def update_linked_questionnaires(
        experiment_id: int = Path(..., description="Numeric ID of the experiment"),
        questionnaire_ids: List[int] = ...,
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
    description="Set the started_at timestamp for a specific experiment.",
    responses={
        404: {"description": "Experiment not found"},
        500: {"description": "Internal server error"},
    }
)
async def set_experiment_started(
        experiment_id: int = Path(..., description="Numeric ID of the experiment"),
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
    description="Set the completed_at timestamp for a specific experiment.",
    responses={
        404: {"description": "Experiment not found"},
        500: {"description": "Internal server error"},
    }
)
async def set_experiment_completed(
        experiment_id: int = Path(..., description="Numeric ID of the experiment"),
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
