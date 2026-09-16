from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import mongo, bcrypt
from ..models.user import create_user_doc, public_user
from ..utils.validators import validate_email, validate_password
from datetime import datetime, timezone

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not email or not password or not full_name:
        return jsonify({"error": "email, password, and full_name are required"}), 400
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    valid_pw, pw_msg = validate_password(password)
    if not valid_pw:
        return jsonify({"error": pw_msg}), 400
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    doc = create_user_doc(email, hashed, full_name)
    result = mongo.db.users.insert_one(doc)
    doc["_id"] = result.inserted_id

    mongo.db.users.create_index("email", unique=True)

    token = create_access_token(identity=str(result.inserted_id))
    return jsonify({"token": token, "user": public_user(doc)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = mongo.db.users.find_one({"email": email})
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.get("is_active", True):
        return jsonify({"error": "Account is deactivated"}), 403

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token, "user": public_user(user)}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Stateless JWT — client discards token; server acknowledges
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    from ..utils.helpers import to_object_id
    user = mongo.db.users.find_one({"_id": to_object_id(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": public_user(user)}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    from ..utils.helpers import to_object_id
    data = request.get_json(silent=True) or {}
    current_pw = data.get("current_password") or ""
    new_pw = data.get("new_password") or ""

    if not current_pw or not new_pw:
        return jsonify({"error": "current_password and new_password are required"}), 400

    valid_pw, pw_msg = validate_password(new_pw)
    if not valid_pw:
        return jsonify({"error": pw_msg}), 400

    user = mongo.db.users.find_one({"_id": to_object_id(user_id)})
    if not user or not bcrypt.check_password_hash(user["password"], current_pw):
        return jsonify({"error": "Current password is incorrect"}), 401

    hashed = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    mongo.db.users.update_one(
        {"_id": to_object_id(user_id)},
        {"$set": {"password": hashed, "updated_at": datetime.now(timezone.utc)}}
    )
    return jsonify({"message": "Password updated successfully"}), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    from ..utils.helpers import to_object_id
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        return jsonify({"error": "full_name is required"}), 400

    mongo.db.users.update_one(
        {"_id": to_object_id(user_id)},
        {"$set": {"full_name": full_name, "updated_at": datetime.now(timezone.utc)}}
    )
    user = mongo.db.users.find_one({"_id": to_object_id(user_id)})
    return jsonify({"user": public_user(user)}), 200
