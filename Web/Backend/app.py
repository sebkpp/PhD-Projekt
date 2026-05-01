from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn


from Backend.routes import register_routes
from Backend.cleanup import start_cleanup_thread
from Backend.models import Base
from Backend.db_session import engine

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    start_cleanup_thread()
    yield


tags_metadata = [
    {"name": "studies", "description": "Manage VR studies — create, update, close, and retrieve studies."},
    {"name": "experiments", "description": "Manage experiments within a study — create, start, complete, and retrieve experiments."},
    {"name": "trials", "description": "Control trial execution — start, end, and retrieve trial data and stimuli assignments."},
    {"name": "participants", "description": "Register participants, manage slot assignments, connection status, and readiness."},
    {"name": "handovers", "description": "Record and retrieve virtual object handover events during trials."},
    {"name": "questionnaires", "description": "Manage questionnaires and retrieve participant responses."},
    {"name": "analysis", "description": "Run statistical analysis on study data — eye tracking, performance, questionnaires, and exports."},
    {"name": "eyetracking", "description": "Save eye-tracking fixation events from the Unity VR application."},
    {"name": "stimuli", "description": "Retrieve available stimulus types used in trial configurations."},
    {"name": "avatar-visibility", "description": "Retrieve avatar visibility configuration options."},
]

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routes(app)

if __name__ == "__main__":
    uvicorn.run("Backend.app:app", host="0.0.0.0", port=5000, log_level="info")