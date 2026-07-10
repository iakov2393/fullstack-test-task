import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    postgres_user: str = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    postgres_db: str = os.environ.get("POSTGRES_DB", "test")
    postgres_host: str = os.environ.get("POSTGRES_HOST", "backend-db")
    pgport: str = os.environ.get("PGPORT", "5433")
    celery_broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://backend-redis:6379/0")

    storage_dir: Path = BASE_DIR / "storage" / "files"

    suspicious_extensions: frozenset = field(
        default_factory=lambda: frozenset({".exe", ".bat", ".cmd", ".sh", ".js"})
    )
    max_file_size_bytes: int = 10 * 1024 * 1024
    upload_chunk_size: int = 1024 * 1024

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.pgport}/{self.postgres_db}"
        )


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
