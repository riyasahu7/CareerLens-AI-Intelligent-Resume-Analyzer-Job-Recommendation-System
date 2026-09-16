from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from ..models.recommendation import create_recommendation_doc, public_recommendation
from ..utils.helpers import to_object_id
from ..services.recommender import recommend_roles
from ..services.learning_plan import generate_learning_plan

recommendations_bp = Blueprint("recommendations", __name__)


@recommendations_bp.route("", methods=["POST"])
@jwt_required()
def generate_recommendations():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    analysis_id = data.get("analysis_id") or ""

    if not analysis_id:
        return jsonify({"error": "analysis_id is required"}), 400

    oid = to_object_id(analysis_id)
    if not oid:
        return jsonify({"error": "Invalid analysis_id"}), 400

    analysis = mongo.db.analyses.find_one({"_id": oid, "user_id": user_id})
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    detected_skills = analysis.get("skills", [])
    role_matches = recommend_roles(detected_skills)

    # Top role missing skills → learning plan
    top_role = role_matches[0] if role_matches else None
    missing = []
    if top_role:
        missing = top_role.missing_required + top_role.missing_nice_to_have[:5]

    # Also collect from job match if available
    if analysis.get("job_match_result"):
        jd_missing = analysis["job_match_result"].get("missing_keywords", [])
        missing = list(dict.fromkeys(missing + jd_missing[:10]))  # dedupe, preserve order

    learning_plan = generate_learning_plan(missing[:15])

    roles_payload = [
        {
            "role": r.role,
            "description": r.description,
            "match_score": r.match_score,
            "matched_required": r.matched_required,
            "missing_required": r.missing_required,
            "matched_nice_to_have": r.matched_nice_to_have,
            "missing_nice_to_have": r.missing_nice_to_have,
            "scoring_note": r.scoring_note,
        }
        for r in role_matches
    ]

    doc = create_recommendation_doc(
        user_id=user_id,
        analysis_id=analysis_id,
        roles=roles_payload,
        skill_gaps=missing,
        learning_plan=learning_plan,
    )
    result = mongo.db.recommendations.insert_one(doc)
    doc["_id"] = result.inserted_id

    return jsonify({"recommendation": public_recommendation(doc)}), 201


@recommendations_bp.route("", methods=["GET"])
@jwt_required()
def list_recommendations():
    user_id = get_jwt_identity()
    analysis_id = request.args.get("analysis_id")
    query = {"user_id": user_id}
    if analysis_id:
        query["analysis_id"] = analysis_id

    docs = list(mongo.db.recommendations.find(query).sort("created_at", -1).limit(20))
    return jsonify({"recommendations": [public_recommendation(d) for d in docs]}), 200


@recommendations_bp.route("/<rec_id>", methods=["GET"])
@jwt_required()
def get_recommendation(rec_id):
    user_id = get_jwt_identity()
    oid = to_object_id(rec_id)
    if not oid:
        return jsonify({"error": "Invalid ID"}), 400
    doc = mongo.db.recommendations.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Recommendation not found"}), 404
    return jsonify({"recommendation": public_recommendation(doc)}), 200
