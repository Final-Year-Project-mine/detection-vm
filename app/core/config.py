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
