from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from ..utils.helpers import to_object_id
from functools import wraps

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": to_object_id(user_id)})
        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def stats():
    user_count = mongo.db.users.count_documents({})
    analysis_count = mongo.db.analyses.count_documents({})
    resume_count = mongo.db.resumes.count_documents({})
    rec_count = mongo.db.recommendations.count_documents({})

    # Recent signups (last 7)
    recent_users = list(mongo.db.users.find(
        {}, {"email": 1, "full_name": 1, "created_at": 1, "role": 1}
    ).sort("created_at", -1).limit(7))

    for u in recent_users:
        u["id"] = str(u.pop("_id"))
        if "created_at" in u:
            u["created_at"] = u["created_at"].isoformat()

    return jsonify({
        "users": user_count,
        "analyses": analysis_count,
        "resumes": resume_count,
        "recommendations": rec_count,
        "recent_users": recent_users,
    }), 200


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = list(mongo.db.users.find(
        {}, {"password": 0}
    ).sort("created_at", -1).limit(100))
    for u in users:
        u["id"] = str(u.pop("_id"))
        if "created_at" in u:
            u["created_at"] = u["created_at"].isoformat()
        if "updated_at" in u:
            u["updated_at"] = u["updated_at"].isoformat()
    return jsonify({"users": users}), 200
