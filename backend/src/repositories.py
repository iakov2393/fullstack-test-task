from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert, StoredFile


class FileRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self) -> list[StoredFile]:
        result = await self._session.execute(select(StoredFile).order_by(StoredFile.created_at.desc()))
        return list(result.scalars().all())

    async def get(self, file_id: str) -> StoredFile | None:
        return await self._session.get(StoredFile, file_id)

    async def add(self, file_item: StoredFile) -> StoredFile:
        self._session.add(file_item)
        await self._session.commit()
        await self._session.refresh(file_item)
        return file_item

    async def save(self, file_item: StoredFile) -> StoredFile:
        """Persists changes on an already-tracked instance."""
        await self._session.commit()
        await self._session.refresh(file_item)
        return file_item

    async def delete(self, file_item: StoredFile) -> None:
        await self._session.delete(file_item)
        await self._session.commit()


class AlertRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self) -> list[Alert]:
        result = await self._session.execute(select(Alert).order_by(Alert.created_at.desc()))
        return list(result.scalars().all())

    async def add(self, alert: Alert) -> Alert:
        self._session.add(alert)
        await self._session.commit()
        await self._session.refresh(alert)
        return alert
