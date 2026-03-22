from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from Backend.services.participant_service import (
    register_participant,
    submit_participant_to_slot,
    get_submission_status, get_participants_by_experiment
)
from Backend.services.connection_service import (
    update_heartbeat,
    get_connection_status,
    player_joined
)
from Backend.models.participant import ParticipantResponse

from sqlalchemy.orm import Session
from Backend.db_session import SessionLocal

router = APIRouter(prefix="/api/participants", tags=["participants"])


class PlayerJoinRequest(BaseModel):
    player_id: str

class HeartbeatRequest(BaseModel):
    player_id: str

class ReadinessRequest(BaseModel):
    slot: str
    ready: bool

class ParticipantCreate(BaseModel):
    age: int
    gender: str
    handedness: str

class SubmitParticipantRequest(BaseModel):
    experiment_id: int
    slot: int
    participant_id: int

readiness_status = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/join",
    status_code=status.HTTP_200_OK,
    summary="Participant join",
    description="Set a participant as joined in the system."
)
async def player_join(
        payload: PlayerJoinRequest
):
    if not player_joined(payload.player_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Participant ID")
    return {"status": "joined", "player_id": payload.player_id}

@router.post(
    "/heartbeat",
    status_code=status.HTTP_200_OK,
    summary="Participant Heartbeat",
    description="Notify the system that a participant is still active."
)
async def player_heartbeat(
        payload: HeartbeatRequest
):
    if not update_heartbeat(payload.player_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Participant ID")
    return {"status": "heartbeat", "player_id": payload.player_id}


@router.get(
    "/connection_status",
    status_code=status.HTTP_200_OK,
    summary="Get Connection Status",
    description="Retrieve the current connection status of participants."
)
async def connection_status():
    status_data = get_connection_status()
    return status_data

@router.get(
    "/readiness_status",
    status_code=status.HTTP_200_OK,
    summary="Get Readiness Status",
    description="Retrieve the readiness status of all slots."

)
async def get_readiness_status():
    return readiness_status

@router.post(
    "/readiness_status",
    status_code=status.HTTP_200_OK,
    summary="Set Readiness Status",
    description="Set the readiness status for a specific slot."
)
async def set_readiness_status(
        payload: ReadinessRequest
):
    readiness_status[payload.slot] = payload.ready
    return {"slot": payload.slot, "ready": payload.ready}

@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new participant",
    description="Register a new participant with age , gender, and handedness."
)
async def register_participant_route(
        payload: ParticipantCreate,
        db: Session = Depends(get_db)
):
    try:
        participant = register_participant(db, payload.age, payload.gender, payload.handedness)
        db.commit()
        return {"participant_id": participant.participant_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/submit",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Submit participant to experiment slot",
    description="Assign a participant to a specific slot in an experiment."
)
async def submit_participant_to_slot_route(
        payload: SubmitParticipantRequest,
        db: Session = Depends(get_db)
):
    try:
        submit_participant_to_slot(db, payload.experiment_id, payload.slot, payload.participant_id)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/status/{experiment_id}/{slot}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get submission status",
    description="Retrieve the submission status of participants for a specific experiment and slot."
)
async def get_submit_status(
        experiment_id: int,
        slot: int,
        db: Session = Depends(get_db)
):
    try:
        status_data = get_submission_status(db, experiment_id, slot)
        return status_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/experiment/{experiment_id}",
    response_model=List[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Get participants by experiment",
    description="Retrieve all participants associated with a specific experiment."
)
async def get_participants_by_experiment_route(
        experiment_id: int,
        db: Session = Depends(get_db)
) -> List[ParticipantResponse]:
    try:
        participants = get_participants_by_experiment(db, experiment_id)
        return participants
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))