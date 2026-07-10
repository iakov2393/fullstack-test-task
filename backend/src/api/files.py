from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from src.api.deps import FileServiceDep
from src.schemas import FileItem, FileUpdate
from src.tasks import scan_file_for_threats

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileItem])
async def list_files(service: FileServiceDep):
    return await service.list_files()


@router.post("", response_model=FileItem, status_code=201)
async def create_file(
    service: FileServiceDep,
    title: str = Form(...),
    file: UploadFile = File(...),
):
    file_item = await service.create_file(title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file(file_id: str, service: FileServiceDep):
    return await service.get_file(file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file(file_id: str, payload: FileUpdate, service: FileServiceDep):
    return await service.update_title(file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, service: FileServiceDep):
    file_item, stored_path = await service.get_download_target(file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: str, service: FileServiceDep):
    await service.delete_file(file_id)
