from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from pydantic import BaseModel

from Backend.db_session import SessionLocal


from Backend.services.questionnaire_response_service import load_questionnaire_responses, save_questionnaire_responses, \
    are_all_questionnaires_in_trial_done, are_all_questionnaires_done, get_questionnaire_responses_for_experiment
from Backend.services.questionnaire_service import get_all_questionnaires, create_questionnaire_with_items, \
    get_questionnaires_for_experiment, get_questionnaires_by_study_id

router = APIRouter(prefix="/questionnaires", tags=["questionnaires"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class QuestionnaireSubmitRequest(BaseModel):
    participant_id: int
    trial_id: int
    questionnaire_name: str
    responses: Dict[str, Any]

class QuestionnaireCreateRequest(BaseModel):
    name: str
    items: List[str]

class QuestionnaireResponseModel(BaseModel):
    status: str
    data: Optional[Any] = None

class QuestionnaireDoneResponse(BaseModel):
    allDone: bool


@router.post(
    "/submit",
    status_code=status.HTTP_200_OK,
    summary="Submit questionnaire responses",
    description="Submit responses for a questionnaire by a participant in a trial."
)
async def submit_questionnaire(
        payload: QuestionnaireSubmitRequest,
        db=Depends(get_db)
):
    try:
        result = save_questionnaire_responses(
            db,
            participant_id=payload.participant_id,
            trial_id=payload.trial_id,
            questionnaire_name=payload.questionnaire_name,
            responses=payload.responses
        )
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/responses",
    response_model=QuestionnaireResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Get questionnaire responses",
    description="Retrieve responses for a questionnaire by participant and trial."
)
async def get_questionnaire_responses(
        participant_id: int = Query(..., description="Participant ID"),
        trial_id: int = Query(..., description="Trial ID"),
        questionnaire_name: str = Query(..., description="Questionnaire name"),
        db=Depends(get_db)
):
    try:
        data = load_questionnaire_responses(db, participant_id, trial_id, questionnaire_name)
        return {"status": "ok", "data": data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new questionnaire",
    description="Create a new questionnaire with a name and items."
)
async def create_questionnaire(
        payload: QuestionnaireCreateRequest,
        db=Depends(get_db)
):
    try:
        questionnaire = create_questionnaire_with_items(db, payload.name, payload.items)
        db.commit()
        return {
            "status": "ok",
            "questionnaire_id": questionnaire.questionnaire_id,
            "name": questionnaire.name,
            "items": [item.item_name for item in questionnaire.items]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List all questionnaires",
    description="Retrieve all available questionnaires."
)
async def get_questionnaires(
        db=Depends(get_db)
):
    try:
        questionnaires = get_all_questionnaires(db)
        return {"status": "ok", "data": questionnaires}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/done",
    response_model=QuestionnaireDoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Check if all questionnaires are done",
    description="Check if all questionnaires are completed for a participant in an experiment."
)
async def check_questionnaires_done(
        participant: int = Query(..., description="Participant ID"),
        experiment: int = Query(..., description="Experiment ID"),
        db=Depends(get_db)
):
    try:
        all_done = are_all_questionnaires_done(db, participant, experiment)
        return {"allDone": all_done}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/trial_done",
    response_model=QuestionnaireDoneResponse,
    status_code=status.HTTP_200_OK,
    summary="Check if all questionnaires in trial are done",
    description="Check if all questionnaires are completed for a participant in a trial."
)
async def check_questionnaires_trial_done(
        participant: int = Query(..., description="Participant ID"),
        trial: int = Query(..., description="Trial ID"),
        db=Depends(get_db)
):
    try:
        all_done = are_all_questionnaires_in_trial_done(db, participant, trial)
        return {"allDone": all_done}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiments/{experiment_id}/participants/{participant_id}/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Get questionnaires for experiment and participant",
    description="Retrieve all questionnaires for a given experiment and participant."
)
async def get_questionnaires_for_experiment_route(
        experiment_id: int = Path(..., description="Experiment ID"),
        participant_id: int = Path(..., description="Participant ID"),
        db=Depends(get_db)
):
    try:
        questionnaires = get_questionnaires_for_experiment(db, experiment_id)
        response = {
            "questionnaires": [q.to_dict() for q in questionnaires]
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get(
    "/experiments/{experiment_id}/questionnaire-responses",
    status_code=status.HTTP_200_OK,
    summary="Get questionnaire responses for experiment",
    description="Retrieve all questionnaire responses for a given experiment."
)
async def get_questionnaire_responses_for_experiment_route(
        experiment_id: int = Path(..., description="Experiment ID"),
        db=Depends(get_db)
):
    try:
        responses = get_questionnaire_responses_for_experiment(db, experiment_id)
        return {"status": "ok", "data": responses}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/study/{study_id}",
    status_code=status.HTTP_200_OK,
    summary="Get questionnaires for study",
    description="Retrieve all questionnaires for a given study."
)
async def get_questionnaires_for_study_route(
        study_id: int = Path(..., description="Study ID"),
        db=Depends(get_db)
):
    try:
        questionnaires = get_questionnaires_by_study_id(db, study_id)
        return questionnaires
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))