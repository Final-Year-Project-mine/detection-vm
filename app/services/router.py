import os
import shutil
from app.services.analyzer import Verdict
from app.core.config import settings

# Mapping configuration to your local constants
QUARANTINE_DIR = settings.quarantine_dir
BACKUP_INBOX_DIR = settings.backup_inbox_dir

def safe_move(src, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(src)
    dest = os.path.join(dest_dir, base)
    shutil.copy2(src, dest)
    # optional: os.remove(src)

def route_file(path, verdict: Verdict):
    if verdict in (Verdict.SUSPICIOUS, Verdict.MALICIOUS):
        safe_move(path, QUARANTINE_DIR)
    elif verdict == Verdict.CLEAN:
        safe_move(path, BACKUP_INBOX_DIR)
