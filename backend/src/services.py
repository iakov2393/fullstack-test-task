import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.exceptions import FileNotFoundError
from src.exceptions import StoredFileMissingError
from src.models import Alert, StoredFile
from src.repositories import AlertRepository, FileRepository
from src.storage import FileStorage


class FileService:
    def __init__(self, repository: FileRepository, storage: FileStorage):
        self._repository = repository
        self._storage = storage

    async def list_files(self) -> list[StoredFile]:
        return await self._repository.list()

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self._repository.get(file_id)
        if not file_item:
            raise FileNotFoundError(file_id)
        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        file_id = uuid4().hex
        stored_name, size = await self._storage.save(file_id, upload_file)

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
            size=size,
            processing_status="uploaded",
        )
        return await self._repository.add(file_item)

    async def update_title(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        return await self._repository.save(file_item)

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        self._storage.delete(file_item.stored_name)
        # DB-level ON DELETE CASCADE (see models.py) removes related alerts too.
        await self._repository.delete(file_item)

    async def get_download_target(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        if not self._storage.exists(file_item.stored_name):
            raise StoredFileMissingError(file_id)
        return file_item, self._storage.path_for(file_item.stored_name)


class AlertService:
    def __init__(self, repository: AlertRepository):
        self._repository = repository

    async def list_alerts(self) -> list[Alert]:
        return await self._repository.list()

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        return await self._repository.add(Alert(file_id=file_id, level=level, message=message))
