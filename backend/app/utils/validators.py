"""
Input validation helpers.
"""

import re
from werkzeug.datastructures import FileStorage


ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024   # 5 MB


def validate_email(email: str) -> bool:
    """Basic email format check."""
    pattern = r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$"
    return bool(re.match(pattern, email, re.I))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Password must be at least 8 chars, contain a letter and a number.
    Returns (is_valid, message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""


def validate_file(file: FileStorage) -> tuple[bool, str]:
    """
    Validate an uploaded file.  Returns (is_valid, error_message).
    """
    if not file or not file.filename:
        return False, "No file selected."

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Only PDF files are accepted. Received: .{ext or 'unknown'}"

    # Read bytes to check size; reset stream afterwards
    file.stream.seek(0, 2)          # seek to end
    size = file.stream.tell()
    file.stream.seek(0)             # reset

    if size > MAX_FILE_SIZE_BYTES:
        mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        return False, f"File exceeds the {mb} MB size limit."

    return True, ""
