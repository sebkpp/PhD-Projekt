from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from sqlalchemy.orm import Session
from Backend.db_session import SessionLocal
from Backend.models.experiment import ExperimentResponse
from Backend.models.participant import ParticipantResponse
from Backend.models.study.study import StudyResponse, StudyCreate, StudyUpdate

from Backend.services.study_service import (
    get_all_studies,
    get_study_by_id,
    create_study,
    update_study,
    delete_study,
    get_experiments_by_study, get_participants_by_study, close_study
)

router = APIRouter(prefix="/studies", tags=["studies"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get(
    "/",
    response_model=List[StudyResponse],
    status_code=status.HTTP_200_OK,
    summary="List all studies",
    description="Retrieve a list of all studies."
)
async def list_studies(
        db: Session = Depends(get_db)
) -> List[StudyResponse]:
    try:
        studies = get_all_studies(db)
        return studies
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{study_id}",
    status_code=status.HTTP_200_OK,
    summary="Get study by ID",
    description="Retrieve a study by its ID."
)
async def get_study_route(
        study_id: int,
        db: Session = Depends(get_db)
):
    study = get_study_by_id(db, study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study.to_dict()


@router.post(
    "/",
    response_model=StudyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new study",
    description="Create a new study with the provided details."
)
async def create_study_route(
        payload: StudyCreate,
        db: Session = Depends(get_db)
) -> StudyResponse:
    try:
        study = create_study(db, payload.model_dump())
        db.commit()
        return study
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/{study_id}",
    response_model=StudyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a study",
    description="Update the details of an existing study by its ID."
)
async def update_study_route(
        study_id: int,
        payload: StudyUpdate,
        db: Session = Depends(get_db)
) -> StudyResponse:
    try:
        updated = update_study(db, study_id, payload.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
        db.commit()
        return updated
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/{study_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a study",
    description="Delete a study by its ID. This operation is irreversible."
)
async def delete_study_route(
        study_id: int,
        db: Session = Depends(get_db)
) -> None:
    try:
        deleted = delete_study(db, study_id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")


@router.get(
    "/{study_id}/experiments",
    response_model=List[ExperimentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all experiments of a study",
    description="Retrieve all experiments associated with a specific study by its ID."
)
async def api_get_experiments_by_study(
        study_id: int,
        db: Session = Depends(get_db)
) -> List[ExperimentResponse]:
    try:
        study = get_study_by_id(db, study_id)
        if not study:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
        experiments = get_experiments_by_study(db, study_id)
        return experiments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{study_id}/participants",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="List all participants of a study",
    description="Retrieve all participants associated with a specific study by its ID."
)
async def api_get_participants_by_study(
        study_id: int,
        db: Session = Depends(get_db)
) -> List[ParticipantResponse]:
    try:
        study = get_study_by_id(db, study_id)
        if not study:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
        participants = get_participants_by_study(db, study_id)
        return participants
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/{study_id}/close",
    response_model=StudyResponse,
    status_code=status.HTTP_200_OK,
    summary="Close a study",
    description="Close a study by setting its status to 'Beendet' and recording the end time."
)
async def close_study_route(
        study_id: int,
        db: Session = Depends(get_db)
) -> StudyResponse:
    try:
        study = close_study(db, study_id)
        if not study:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Study not found or already finished")
        db.commit()
        return study
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
