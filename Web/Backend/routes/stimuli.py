from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from Backend.db_session import SessionLocal
from Backend.services.stimuli_service import get_all_stimuli
router = APIRouter(prefix="/stimuli", tags=["stimuli"])

class StimulusResponse(BaseModel):
    id: int
    name: str
    type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=List[StimulusResponse],
    status_code=status.HTTP_200_OK,
    summary="List all stimuli types",
    description="Retrieve a list of all available stimuli types.",
    responses={500: {"description": "Internal server error"}},
)
async def list_stimuli(
        db=Depends(get_db)
) -> List[StimulusResponse]:
    try:
        data = get_all_stimuli(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")