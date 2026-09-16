"""
User model helpers.  MongoDB documents are plain dicts; these helpers
provide consistent structure and safe serialisation.
"""

from datetime import datetime, timezone
from bson import ObjectId


def create_user_doc(email: str, hashed_password: str, full_name: str, role: str = "user") -> dict:
    """Return a new user document ready to be inserted into MongoDB."""
    return {
        "email": email.lower().strip(),
        "password": hashed_password,        # bcrypt hash — never plaintext
        "full_name": full_name.strip(),
        "role": role,                        # "user" | "admin"
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_active": True,
    }


def public_user(user_doc: dict) -> dict:
    """Return a safe public representation (no password hash)."""
    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "full_name": user_doc["full_name"],
        "role": user_doc.get("role", "user"),
        "created_at": user_doc["created_at"].isoformat(),
        "is_active": user_doc.get("is_active", True),
    }
