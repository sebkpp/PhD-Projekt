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


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routes (Module müssen `router: APIRouter` exportieren)
register_routes(app)

if __name__ == "__main__":
    uvicorn.run("Backend.app:app", host="0.0.0.0", port=5000, log_level="info")