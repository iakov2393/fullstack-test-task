import asyncio

from celery import Celery

from src.config import settings
from src.database import async_session_maker
from src.processing import extract_metadata, scan_for_threats
from src.repositories import AlertRepository, FileRepository
from src.services import AlertService
from src.storage import FileStorage

_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    """Reuses a single event loop across task invocations in this worker
    process instead of creating a new one every time."""
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


celery_app = Celery("file_tasks", broker=settings.celery_broker_url, backend=settings.celery_broker_url)


async def _scan_file_for_threats(file_id: str) -> None:
    async with async_session_maker() as session:
        repository = FileRepository(session)
        file_item = await repository.get(file_id)
        if not file_item:
            return

        file_item.processing_status = "processing"
        result = scan_for_threats(file_item.original_name, file_item.size, file_item.mime_type)
        file_item.scan_status = result.status
        file_item.scan_details = result.details
        file_item.requires_attention = result.requires_attention
        await repository.save(file_item)

    extract_file_metadata.delay(file_id)


async def _extract_file_metadata(file_id: str) -> None:
    storage = FileStorage()
    async with async_session_maker() as session:
        repository = FileRepository(session)
        file_item = await repository.get(file_id)
        if not file_item:
            return

        if not storage.exists(file_item.stored_name):
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await repository.save(file_item)
            send_file_alert.delay(file_id)
            return

        stored_path = storage.path_for(file_item.stored_name)
        file_item.metadata_json = extract_metadata(
            stored_path, file_item.original_name, file_item.mime_type, file_item.size,
        )
        file_item.processing_status = "processed"
        await repository.save(file_item)

    send_file_alert.delay(file_id)


async def _send_file_alert(file_id: str) -> None:
    async with async_session_maker() as session:
        file_item = await FileRepository(session).get(file_id)
        if not file_item:
            return

        alert_service = AlertService(AlertRepository(session))
        if file_item.processing_status == "failed":
            await alert_service.create_alert(file_id, level="critical", message="File processing failed")
        elif file_item.requires_attention:
            await alert_service.create_alert(
                file_id, level="warning", message=f"File requires attention: {file_item.scan_details}"
            )
        else:
            await alert_service.create_alert(file_id, level="info", message="File processed successfully")


@celery_app.task
def scan_file_for_threats(file_id: str) -> None:
    run_in_worker_loop(_scan_file_for_threats(file_id))


@celery_app.task
def extract_file_metadata(file_id: str) -> None:
    run_in_worker_loop(_extract_file_metadata(file_id))


@celery_app.task
def send_file_alert(file_id: str) -> None:
    run_in_worker_loop(_send_file_alert(file_id))
