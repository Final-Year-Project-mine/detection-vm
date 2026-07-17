# Detection VM Refactor Documentation

## Overview

The original Detection VM consisted of three standalone Python scripts:

```text
detector_watchdog.py
analyzer.py
router.py
```

These scripts worked correctly but were not organized as a service. The goal of the refactor was **not to change functionality**, but to reorganize the Detection VM into a maintainable FastAPI-based microservice while preserving all existing behavior.

---

# Original Architecture

```text
Production Files
       |
       v
detector_watchdog.py
       |
       v
analyzer.py
       |
       v
router.py
      / \
     /   \
    v     v
Backup   Quarantine
```

---

# Refactor Goals

The refactor focused on:

* Keeping the existing detection logic unchanged
* Keeping the watcher autonomous
* Introducing FastAPI as a service host
* Preparing the VM for future dashboard integration
* Separating responsibilities into logical modules

---

# Current Detection Service Structure

```text
detection_vm/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── detection.py
│   │
│   ├── services/
│   │   ├── analyzer.py
│   │   ├── router.py
│   │   └── watcher.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── core/
│       └── config.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# Responsibilities

## watcher.py

Responsible for:

* Monitoring the production directory
* Detecting new or modified files
* Triggering analysis
* Triggering routing
* Logging verdicts

Does NOT:

* Make security decisions
* Move files directly

---

## analyzer.py

Responsible for:

* Entropy analysis
* Suspicious extension detection
* Verdict generation

Returns:

```python
Verdict.CLEAN
Verdict.SUSPICIOUS
Verdict.MALICIOUS
```

Does NOT:

* Move files
* Write logs

---

## router.py

Responsible for:

* Copying files to Backup Inbox
* Copying files to Quarantine

Does NOT:

* Analyze files
* Log decisions

---

## FastAPI Layer

Responsible for:

* Health checks
* Service information
* Manual analysis endpoints
* Future dashboard integration

Does NOT:

* Perform core detection logic

---

# Runtime Flow

When a new file appears:

```text
/mnt/prod/Prod_Files
          |
          v
      Watcher
          |
          v
      Analyzer
          |
          v
       Verdict
          |
    +-----+------+
    |            |
    v            v
 Backup     Quarantine
```

---

# Configuration

## .env

```env
WATCH_DIR=/mnt/prod/Prod_Files
BACKUP_INBOX_DIR=/mnt/backup_inbox
QUARANTINE_DIR=/mnt/quarantine
LOG_FILE=/var/log/detector.log
```

---

## app/core/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    watch_dir: str = "/mnt/prod/Prod_Files"

    backup_inbox_dir: str = "/mnt/backup_inbox"

    quarantine_dir: str = "/mnt/quarantine"

    log_file: str = "/var/log/detector.log"

    service_name: str = "Detection Service"

    class Config:
        env_file = ".env"


settings = Settings()
```

---

# FastAPI Application

## app/main.py

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.watcher import (
    start_watcher,
    stop_watcher
)

from app.api.detection import router as detection_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_watcher()

    yield

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
```

---

# Watcher Integration

The watcher starts automatically when FastAPI starts.

## watcher.py

```python
from watchdog.observers import Observer

observer = None


def start_watcher():
    global observer

    if observer is not None:
        return

    event_handler = Handler()

    observer = Observer()
    observer.schedule(
        event_handler,
        settings.watch_dir,
        recursive=True,
    )

    observer.start()

    print("[WATCHER] Started")


def stop_watcher():
    global observer

    if observer is None:
        return

    observer.stop()
    observer.join()

    observer = None

    print("[WATCHER] Stopped")
```

---

# API Layer

## app/api/detection.py

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {
        "service": "detection",
        "status": "healthy"
    }
```

---

## Service Info Endpoint

```python
@router.get("/service-info")
def service_info():
    return {
        "watch_dir": settings.watch_dir,
        "backup_inbox": settings.backup_inbox_dir,
        "quarantine_dir": settings.quarantine_dir,
        "log_file": settings.log_file,
    }
```

---

# Request Models

## app/models/schemas.py

```python
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    path: str


class AnalyzeResponse(BaseModel):
    verdict: str
```

---

# Analyze Endpoint

```python
from app.services.analyzer import analyze_file
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(req: AnalyzeRequest):
    verdict = analyze_file(req.path)

    return AnalyzeResponse(
        verdict=verdict.name
    )
```

---

# Example Execution

Command:

```bash
echo "test" | sudo tee /mnt/prod/Prod_Files/test2.txt > /dev/null
```

---

## Step 1

File created:

```text
/mnt/prod/Prod_Files/test2.txt
```

---

## Step 2

Watcher detects creation event.

---

## Step 3

Analyzer evaluates file.

Filename:

```text
test2.txt
```

No suspicious extension.

Entropy not suspicious.

Verdict:

```text
CLEAN
```

---

## Step 4

Router copies file to:

```text
/mnt/backup_inbox/test2.txt
```

---

## Step 5

Log entry written:

```text
timestamp,
/mnt/prod/Prod_Files/test2.txt,
CLEAN
```

to:

```text
/var/log/detector.log
```

---

# Final Architecture

```text
                Detection VM

      File Arrives (/mnt/prod/Prod_Files)
                    |
                    v
              Watcher Service
                    |
                    v
               Analyzer
                    |
                    v
                Router
               /      \
              /        \
             v          v
     Backup Inbox   Quarantine

                    ^
                    |
                FastAPI
                    |
       Health / Info / Analyze APIs
```

---

# Key Design Decision

The watcher remains autonomous.

FastAPI is not responsible for monitoring files.

Instead:

```text
Watcher
    ↓
Analyzer
    ↓
Router
```

continues to operate independently, while FastAPI provides observability, management endpoints, and future dashboard integration.

This preserves the original behavior while transforming the Detection VM into a maintainable microservice.
