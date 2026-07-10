from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.repositories import AlertRepository, FileRepository
from src.services import AlertService, FileService
from src.storage import FileStorage

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_file_service(session: SessionDep) -> FileService:
    return FileService(FileRepository(session), FileStorage())


def get_alert_service(session: SessionDep) -> AlertService:
    return AlertService(AlertRepository(session))


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]
