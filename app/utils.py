import string
import magic
from slugify import slugify
from typing import Tuple
from fastapi import UploadFile
import os
import uuid

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'text/csv',                       # CSV files
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel files (.xlsx)
    'application/vnd.ms-excel',       # Excel files (.xls)
}

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def sanitize_filename(filename: str) -> str:
    name, ext = filename.rsplit('.', 1)
    safe_name = slugify(name)
    return f"{safe_name}.{ext}"


def validate_mime_type(file_content: bytes) -> Tuple[bool, str]:
    """
    Validate the MIME type of the file content.
    Returns True and the MIME type if valid, otherwise False.
    """
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_content)
    return mime_type in ALLOWED_MIME_TYPES, mime_type

def is_allowed_extension(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_total_file_size(file: UploadFile) -> int:
    """
    Helper function to estimate total file size by reading the header
    """
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)  # Reset file pointer after getting the size
    return size

def generate_file_id() -> str:
    """
    Generate a unique file ID using UUID4.
    """
    return str(uuid.uuid4())