from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


class AppError(Exception):
    """Base class for domain-level errors, framework-agnostic on purpose."""


class FileNotFoundError(AppError):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"File {file_id} not found")


class StoredFileMissingError(AppError):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Stored file for {file_id} not found on disk")


class EmptyFileError(AppError):
    def __init__(self):
        super().__init__("File is empty")


_STATUS_BY_ERROR: dict[type[AppError], int] = {
    FileNotFoundError: status.HTTP_404_NOT_FOUND,
    StoredFileMissingError: status.HTTP_404_NOT_FOUND,
    EmptyFileError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        status_code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})
