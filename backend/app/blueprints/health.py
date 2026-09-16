"""
Health check endpoint.
"""

from flask import Blueprint, jsonify
from ..extensions import mongo

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    db_ok = False
    try:
        mongo.db.command("ping")
        db_ok = True
    except Exception:
        pass

    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "service": "CareerLens AI API",
    }), 200 if db_ok else 503
