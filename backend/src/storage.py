from pathlib import Path

from fastapi import UploadFile

from src.config import settings
from src.exceptions import EmptyFileError


class FileStorage:
    """All interactions with the on-disk file storage go through here."""

    def __init__(self, base_dir: Path = settings.storage_dir):
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, stored_name: str) -> Path:
        return self._base_dir / stored_name

    def exists(self, stored_name: str) -> bool:
        return self.path_for(stored_name).exists()

    async def save(self, file_id: str, upload_file: UploadFile) -> tuple[str, int]:
        """Streams the upload to disk in chunks instead of reading it fully
        into memory first (as the previous implementation did)."""
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        destination = self.path_for(stored_name)

        size = 0
        with destination.open("wb") as buffer:
            while chunk := await upload_file.read(settings.upload_chunk_size):
                size += len(chunk)
                buffer.write(chunk)

        if size == 0:
            destination.unlink(missing_ok=True)
            raise EmptyFileError()

        return stored_name, size

    def delete(self, stored_name: str) -> None:
        self.path_for(stored_name).unlink(missing_ok=True)
