from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel


from Backend.db_session import SessionLocal
from Backend.services.avatar_visibility_service import get_all_avatar_visibility

router = APIRouter(prefix="/avatar-visibility", tags=["avatar-visibility"])

class AvatarVisibilityResponse(BaseModel):
    avatar_id: int
    visible: bool

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/",
    response_model=List[AvatarVisibilityResponse],
    status_code=status.HTTP_200_OK,
    summary="List all avatar visibility entries",
    description="Retrieve a list of all avatar visibility entries."
)
async def get_avatar_visibility_route(
        db=Depends(get_db)
) -> List[AvatarVisibilityResponse]:
    try:
        data = get_all_avatar_visibility(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")