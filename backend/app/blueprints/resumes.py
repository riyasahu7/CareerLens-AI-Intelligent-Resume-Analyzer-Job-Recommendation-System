import os, uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from ..models.resume import create_resume_doc, public_resume
from ..utils.validators import validate_file
from ..utils.helpers import safe_filename, to_object_id
from ..services.pdf_extractor import extract_text

resumes_bp = Blueprint("resumes", __name__)

@resumes_bp.route("", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    valid, err = validate_file(file)
    if not valid:
        return jsonify({"error": err}), 400

    file_bytes = file.read()
    extraction = extract_text(file_bytes)

    original_name = file.filename
    safe_name = safe_filename(original_name)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"

    # Optionally persist file to disk (disabled by default for privacy)
    store_files = os.environ.get("STORE_RESUME_FILES", "false").lower() == "true"
    if store_files:
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        with open(upload_path, "wb") as f:
            f.write(file_bytes)

    doc = create_resume_doc(
        user_id=user_id,
        filename=unique_name,
        original_filename=original_name,
        extracted_text=extraction.text,
        file_size_bytes=len(file_bytes),
        extraction_method=extraction.method,
        extraction_success=extraction.success,
    )
    result = mongo.db.resumes.insert_one(doc)
    doc["_id"] = result.inserted_id

    response = public_resume(doc)
    if not extraction.success:
        response["warning"] = extraction.warning

    return jsonify({"resume": response}), 201


@resumes_bp.route("", methods=["GET"])
@jwt_required()
def list_resumes():
    user_id = get_jwt_identity()
    docs = list(mongo.db.resumes.find({"user_id": user_id}).sort("created_at", -1))
    return jsonify({"resumes": [public_resume(d) for d in docs]}), 200


@resumes_bp.route("/<resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id):
    user_id = get_jwt_identity()
    oid = to_object_id(resume_id)
    if not oid:
        return jsonify({"error": "Invalid resume ID"}), 400
    doc = mongo.db.resumes.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Resume not found"}), 404
    return jsonify({"resume": public_resume(doc)}), 200


@resumes_bp.route("/<resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    user_id = get_jwt_identity()
    oid = to_object_id(resume_id)
    if not oid:
        return jsonify({"error": "Invalid resume ID"}), 400
    result = mongo.db.resumes.delete_one({"_id": oid, "user_id": user_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Resume not found"}), 404
    # Also delete linked analyses
    mongo.db.analyses.delete_many({"resume_id": resume_id, "user_id": user_id})
    return jsonify({"message": "Resume and linked analyses deleted"}), 200
