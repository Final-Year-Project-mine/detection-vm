import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.services.analyzer import analyze_file
from app.services.router import route_file
from app.core.config import settings

# Setup basic logging configuration
WATCH_DIR = settings.watch_dir
LOG_FILE = settings.log_file

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(created).6f,%(message)s"
)

# Global tracker for the observer thread
observer = None


class Handler(FileSystemEventHandler):
    def wait_for_file_stability(self, path):
        """Ensures the file has finished writing before analysis begins."""
        try:
            last_size = -1
            while True:
                current_size = os.path.getsize(path)
                if current_size == last_size:
                    break
                last_size = current_size
                time.sleep(1)
            return True
        except FileNotFoundError:
            return False

    def process(self, path):
        if os.path.basename(path).startswith('.'):
            return

        if not self.wait_for_file_stability(path):
            return

        try:
            verdict = analyze_file(path)
            route_file(path, verdict)
            
            # 1. Custom logger execution
            from app.core.logger import logger
            logger.info(
                f"{path} -> {verdict.name}"
            )
            
            # 2. Update Runtime Statistics
            from app.core.stats import stats
            from datetime import datetime
            
            stats["processed"] += 1
            if verdict.name == "CLEAN":
                stats["clean"] += 1
            elif verdict.name == "SUSPICIOUS":
                stats["suspicious"] += 1
            elif verdict.name == "MALICIOUS":
                stats["malicious"] += 1
            
            stats["last_detection"] = datetime.utcnow().isoformat()

        except Exception as e:
            print(f"[-] Error processing {path}: {str(e)}")

    def on_created(self, event):
        if not event.is_directory:
            self.process(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process(event.src_path)


# --- Lifespan Control Functions ---

def start_watcher():
    global observer

    if observer is not None:
        print("[WATCHER] Already running.")
        return

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()
    print("[WATCHER] Started and monitoring background folder.")


def stop_watcher():
    global observer

    if observer is None:
        print("[WATCHER] Not running.")
        return

    observer.stop()
    observer.join()
    observer = None
    print("[WATCHER] Stopped.")
