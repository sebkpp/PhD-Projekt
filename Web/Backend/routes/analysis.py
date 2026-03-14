from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from Backend.db_session import SessionLocal
from Backend.services.data_analysis.eye_tracking_analysis_service import (
    analyze_experiment_eye_tracking,
    analyze_study_eye_tracking,
)
from Backend.services.data_analysis.performance_analysis_service import (
    analyze_experiment_performance,
    analyze_study_performance,
)
from Backend.services.data_analysis.questionnaire_analysis_service import (
    analyze_experiment_questionnaires,
    analyze_study_questionnaires,
)
from Backend.services.data_analysis.correlation_service import calc_correlation_matrix
from Backend.services.data_analysis.cross_study_service import compare_studies_descriptive
from Backend.services.data_analysis.exploratory_service import run_pca, run_clustering

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
    description="Return questionnaire analysis for all studies/experiments (not implemented).",
)
async def questionnaire_analysis():
    return None


@router.get(
    "/study/{study_id}/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Questionnaire analysis for a study",
    description="Return questionnaire analysis aggregated across all experiments in a study.",
)
async def study_questionnaires_analysis(study_id: int, db=Depends(get_db)):
    try:
        result = analyze_study_questionnaires(db, study_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiment/{experiment_id}/questionnaires",
    status_code=status.HTTP_200_OK,
    summary="Questionnaire analysis for an experiment",
    description="Return questionnaire analysis for a specific experiment.",
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis (all)",
    description="Return performance analysis for all studies/experiments (not implemented).",
)
async def all_performance_analysis():
    return None


@router.get(
    "/study/{study_id}/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis for a study",
    description="Return handover performance analysis aggregated across all experiments in a study.",
)
async def study_performance_analysis(study_id: int, db=Depends(get_db)):
    try:
        result = analyze_study_performance(db, study_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiment/{experiment_id}/performance",
    status_code=status.HTTP_200_OK,
    summary="Performance analysis for an experiment",
    description="Return performance analysis for a specific experiment.",
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis (all)",
    description="Return eyetracking analysis for all studies/experiments (not implemented).",
)
async def all_eyetracking_analysis():
    return None


@router.get(
    "/study/{study_id}/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis for a study",
    description="Return eyetracking AOI analysis aggregated by stimulus condition across all experiments in a study.",
)
async def study_eyetracking_analysis(study_id: int, db=Depends(get_db)):
    try:
        result = analyze_study_eye_tracking(db, study_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/experiment/{experiment_id}/eyetracking",
    status_code=status.HTTP_200_OK,
    summary="Eyetracking analysis for an experiment",
    description="Return eyetracking AOI analysis for a specific experiment.",
)
async def experiment_eyetracking_analysis(experiment_id: int, db=Depends(get_db)):
    try:
        result = analyze_experiment_eye_tracking(db, experiment_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Result")
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ---------------------------------------------------------------------------
# New endpoints: eye-tracking (hyphenated alias), correlation, cross-study,
# PCA, clustering
# ---------------------------------------------------------------------------

@router.get(
    "/study/{study_id}/eye-tracking",
    status_code=status.HTTP_200_OK,
    summary="Eye-tracking analysis for a study (hyphenated alias)",
    description="Return eyetracking AOI analysis aggregated across all experiments in a study.",
)
async def get_study_eye_tracking(study_id: int, db=Depends(get_db)):
    result = analyze_study_eye_tracking(db, study_id)
    if not result:
        raise HTTPException(status_code=404, detail="No eye-tracking data found")
    return result


class CorrelationRequest(BaseModel):
    variables: dict[str, list[float]]


@router.post(
    "/correlation",
    status_code=status.HTTP_200_OK,
    summary="Correlation matrix",
    description="Compute pairwise Pearson correlations for the supplied variables.",
)
async def post_correlation(request: CorrelationRequest):
    if len(request.variables) < 2:
        raise HTTPException(status_code=400, detail="At least 2 variables required")
    result = calc_correlation_matrix(request.variables)
    return result


class CrossStudyRequest(BaseModel):
    study_data: dict[str, list[float]]
    metric: str = "transfer_duration_ms"


@router.post(
    "/cross-study",
    status_code=status.HTTP_200_OK,
    summary="Cross-study descriptive comparison",
    description="Descriptive comparison of a metric across multiple studies/conditions.",
)
async def post_cross_study(request: CrossStudyRequest):
    result = compare_studies_descriptive(request.study_data, request.metric)
    return result


class PCARequest(BaseModel):
    data: dict[str, list[float]]
    n_components: int = 2


@router.post(
    "/pca",
    status_code=status.HTTP_200_OK,
    summary="Principal Component Analysis",
    description="Run PCA on the supplied variables.",
)
async def post_pca(request: PCARequest):
    result = run_pca(request.data, n_components=request.n_components)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="PCA requires at least 2 variables with equal length",
        )
    return result


class ClusteringRequest(BaseModel):
    data: dict[str, list[float]]
    n_clusters: int = 3


@router.post(
    "/clustering",
    status_code=status.HTTP_200_OK,
    summary="Hierarchical clustering",
    description="Run agglomerative clustering on the supplied variables.",
)
async def post_clustering(request: ClusteringRequest):
    result = run_clustering(request.data, n_clusters=request.n_clusters)
    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Clustering requires at least 2 variables",
        )
    return result


# ─── Export-Endpunkte ───────────────────────────────────────────────────────

import io
from fastapi.responses import StreamingResponse
from Backend.services.data_analysis.export_service import export_handovers_csv, export_handovers_xlsx
from Backend.db.handover_repository import HandoverRepository


@router.get(
    "/study/{study_id}/export/csv",
    summary="Export handover data as CSV",
    description="Export all handover data for a study as a UTF-8 encoded CSV file.",
)
async def export_study_csv(study_id: int, db: Session = Depends(get_db)):
    repo = HandoverRepository(db)
    handovers = repo.get_handovers_by_study(study_id)
    if not handovers:
        raise HTTPException(status_code=404, detail="No handover data found")
    data = [h.to_dict() for h in handovers]
    csv_bytes = export_handovers_csv(data)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=handovers_study_{study_id}.csv"},
    )


@router.get(
    "/study/{study_id}/export/xlsx",
    summary="Export handover data as XLSX",
    description="Export all handover data for a study as an Excel (XLSX) file.",
)
async def export_study_xlsx(study_id: int, db: Session = Depends(get_db)):
    repo = HandoverRepository(db)
    handovers = repo.get_handovers_by_study(study_id)
    if not handovers:
        raise HTTPException(status_code=404, detail="No handover data found")
    data = [h.to_dict() for h in handovers]
    xlsx_bytes = export_handovers_xlsx(data)
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=handovers_study_{study_id}.xlsx"},
    )
