from dataclasses import dataclass
from pathlib import Path

from src.config import settings

_PDF_PAGE_MARKER = b"/Type /Page"


@dataclass(frozen=True)
class ScanResult:
    status: str
    details: str
    requires_attention: bool


def scan_for_threats(original_name: str, size: int, mime_type: str) -> ScanResult:
    """Same rules as before, extracted into a pure/testable function."""
    reasons: list[str] = []
    extension = Path(original_name).suffix.lower()

    if extension in settings.suspicious_extensions:
        reasons.append(f"suspicious extension {extension}")

    if size > settings.max_file_size_bytes:
        reasons.append("file is larger than 10 MB")

    if extension == ".pdf" and mime_type not in {"application/pdf", "application/octet-stream"}:
        reasons.append("pdf extension does not match mime type")

    return ScanResult(
        status="suspicious" if reasons else "clean",
        details=", ".join(reasons) if reasons else "no threats found",
        requires_attention=bool(reasons),
    )


def extract_metadata(stored_path: Path, original_name: str, mime_type: str, size: int) -> dict:
    """Same metadata fields as before, but streamed rather than reading
    the whole file into memory (relevant for large text/PDF files)."""
    metadata: dict = {
        "extension": Path(original_name).suffix.lower(),
        "size_bytes": size,
        "mime_type": mime_type,
    }

    if mime_type.startswith("text/"):
        line_count = 0
        char_count = 0
        with stored_path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line_count += 1
                char_count += len(line)
        metadata["line_count"] = line_count
        metadata["char_count"] = char_count

    elif mime_type == "application/pdf":
        count = 0
        overlap = b""
        with stored_path.open("rb") as fh:
            while chunk := fh.read(1024 * 1024):
                buffer = overlap + chunk
                count += buffer.count(_PDF_PAGE_MARKER)
                overlap = buffer[-len(_PDF_PAGE_MARKER):]
        metadata["approx_page_count"] = max(count, 1)

    return metadata
