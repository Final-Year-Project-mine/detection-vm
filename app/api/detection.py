from fastapi import APIRouter
from app.services.analyzer import analyze_file
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
)
from app.core.config import settings



router = APIRouter()


@router.get("/health")
@router.get("/api/health")
def health():
    return {
        "service": "detection",
        "status": "healthy",
    }


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(req: AnalyzeRequest):
    verdict = analyze_file(req.path)

    return AnalyzeResponse(
        verdict=verdict.name
    )


@router.get("/service-info")
def service_info():
    return {
        "watch_dir": settings.watch_dir,
        "backup_inbox": settings.backup_inbox_dir,
        "quarantine_dir": settings.quarantine_dir,
        "log_file": settings.log_file,
    }
