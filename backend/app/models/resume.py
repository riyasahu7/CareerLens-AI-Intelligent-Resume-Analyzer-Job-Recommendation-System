"""
Resume document schema helpers.
Text content is stored for analysis; the original file is NOT stored
permanently unless STORE_RESUME_FILES=true in environment.
"""

from datetime import datetime, timezone


def create_resume_doc(
    user_id: str,
    filename: str,
    original_filename: str,
    extracted_text: str,
    file_size_bytes: int,
    extraction_method: str,
    extraction_success: bool,
) -> dict:
    return {
        "user_id": user_id,
        "filename": filename,                   # sanitised filename (no path)
        "original_filename": original_filename,
        "extracted_text": extracted_text,
        "file_size_bytes": file_size_bytes,
        "extraction_method": extraction_method, # "pdfplumber" | "pypdf2" | "failed"
        "extraction_success": extraction_success,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def public_resume(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "filename": doc["filename"],
        "original_filename": doc["original_filename"],
        "file_size_bytes": doc["file_size_bytes"],
        "extraction_success": doc["extraction_success"],
        "extraction_method": doc["extraction_method"],
        "created_at": doc["created_at"].isoformat(),
        "has_text": bool(doc.get("extracted_text", "").strip()),
    }
