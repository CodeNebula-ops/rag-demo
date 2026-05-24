import os
import uuid
from pathlib import Path

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


def validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")
    return ext


def generate_storage_path(filename: str) -> str:
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return os.path.join(settings.upload_dir, unique_name)


def get_file_size_mb(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)
