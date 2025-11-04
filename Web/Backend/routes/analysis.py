from fastapi import APIRouter, HTTPException, status, Depends

from Backend.db_session import SessionLocal
from Backend.services.data_analysis.performance_analysis_service import analyze_experiment_performance
from Backend.services.data_analysis.questionnaire_analysis_service import analyze_experiment_questionnaires

router = APIRouter(prefix="/analysis", tags=["analysis"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Questionnaire analysis (all)",
    description="Return questionnaire analysis for all studies/experiments (not implemented)."
)
async def questionnaire_analysis():
    return None


@router.get(
    "/study/{study_id}/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Questionnaire analysis for a study",
    description="Return questionnaire analysis for a specific study (not implemented)."
)
async def study_questionnaires_analysis(study_id: int):
    return None


@router.get(
    "/experiment/{experiment_id}/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Questionnaire analysis for an experiment",
    description="Return questionnaire analysis for a specific experiment."
)
async def experiment_questionnaire_analysis(
        experiment_id: int,
        db=Depends(get_db)
):
    try:
        result = analyze_experiment_questionnaires(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis (all)",
    description="Return performance analysis for all studies/experiments (not implemented)."
)
async def all_performance_analysis():
    return None

@router.get(
    "/study/{study_id}/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis for a study",
    description="Return performance analysis for a specific study (not implemented)."
)
async def study_performance_analysis(study_id: int):
    return None

@router.get(
    "/experiment/{experiment_id}/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis for an experiment",
    description="Return performance analysis for a specific experiment."
)
async def experiment_performance_analysis(
        experiment_id: int,
        db=Depends(get_db)
):
    try:
        result = analyze_experiment_performance(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis (all)",
    description="Return eyetracking analysis for all studies/experiments (not implemented)."
)
async def all_eyetracking_analysis():
    return None

@router.get(
    "/study/{study_id}/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis for a study",
    description="Return eyetracking analysis for a specific study (not implemented)."
)
async def study_eyetracking_analysis(study_id: int):
    return None

@router.get(
    "/experiment/{experiment_id}/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis for an experiment",
    description="Return eyetracking analysis for a specific experiment (not implemented)."
)
async def experiment_eyetracking_analysis(experiment_id: int):
    return None