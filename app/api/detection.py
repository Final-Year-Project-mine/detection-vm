import os
from fastapi import APIRouter
from app.services.analyzer import analyze_file
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
)
from app.core.config import settings
from app.core.stats import stats



router = APIRouter()


@router.get("/health")
@router.get("/api/health")
def health():

    return {
        "service": "detection",

        "watch_dir_exists":
            os.path.exists(settings.watch_dir),

        "backup_inbox_exists":
            os.path.exists(settings.backup_inbox_dir),

        "quarantine_exists":
            os.path.exists(settings.quarantine_dir),

        "status": "healthy"
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

@router.get("/stats")
def get_stats():
    return stats
