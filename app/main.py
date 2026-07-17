from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.watcher import start_watcher, stop_watcher
from app.api.detection import router as detection_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when Uvicorn boots up
    start_watcher()
    
    yield
    
    # This runs when Uvicorn shuts down (e.g., CTRL+C)
    stop_watcher()

app = FastAPI(
    title="Detection Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    detection_router,
    prefix="/api",
    tags=["Detection"],
)
