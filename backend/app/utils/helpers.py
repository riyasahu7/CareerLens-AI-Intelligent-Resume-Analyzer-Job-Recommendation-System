"""
Miscellaneous helper utilities.
"""

import re
import unicodedata
from bson import ObjectId


def safe_filename(filename: str) -> str:
    """
    Return a filesystem-safe version of a filename.
    Strips path components, replaces special characters.
    """
    # Keep only the basename
    filename = filename.replace("\\", "/").split("/")[-1]
    # Normalise unicode
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    # Replace anything other than alphanumeric, dash, underscore, dot
    filename = re.sub(r"[^\w.\-]", "_", filename)
    # Prevent double dots (path traversal)
    filename = re.sub(r"\.{2,}", ".", filename)
    return filename.strip("._") or "upload"


def to_object_id(id_str: str) -> ObjectId | None:
    """Safely convert a string to a MongoDB ObjectId."""
    try:
        return ObjectId(id_str)
    except Exception:
        return None


def json_response(data: dict, status: int = 200):
    """Convenience wrapper — blueprints use jsonify directly."""
    from flask import jsonify
    return jsonify(data), status
