from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from ..models.analysis import create_analysis_doc, public_analysis
from ..utils.helpers import to_object_id
from ..services.skill_extractor import extract_skills
from ..services.ats_scorer import score_resume, detect_sections
from ..services.tfidf_service import compute_similarity
from ..services.llm_service import get_resume_feedback, is_llm_enabled

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/resume", methods=["POST"])
@jwt_required()
def analyze_resume():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    resume_id = data.get("resume_id") or ""
    job_description = (data.get("job_description") or "").strip() or None

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400

    oid = to_object_id(resume_id)
    if not oid:
        return jsonify({"error": "Invalid resume_id"}), 400

    resume_doc = mongo.db.resumes.find_one({"_id": oid, "user_id": user_id})
    if not resume_doc:
        return jsonify({"error": "Resume not found"}), 404

    if not resume_doc.get("extraction_success") or not resume_doc.get("extracted_text", "").strip():
        return jsonify({
            "error": "Cannot analyse this resume",
            "detail": "Text extraction failed or returned empty. Please upload a text-based PDF."
        }), 422

    text = resume_doc["extracted_text"]

    # Skills
    skill_result = extract_skills(text)

    # Sections
    sections = detect_sections(text)

    # Job match (TF-IDF) if JD provided
    job_match = None
    job_keywords = None
    if job_description:
        sim = compute_similarity(text, job_description)
        job_keywords = sim.top_job_keywords
        job_match = {
            "tfidf_score": sim.score,
            "matched_keywords": sim.matched_keywords,
            "missing_keywords": sim.missing_keywords,
            "note": sim.note,
        }

    # ATS score
    ats = score_resume(
        resume_text=text,
        detected_skills=skill_result.skills,
        job_description=job_description,
        job_keywords=job_keywords,
    )

    # LLM / rule-based feedback
    feedback = get_resume_feedback(text, job_description)

    doc = create_analysis_doc(
        user_id=user_id,
        resume_id=resume_id,
        resume_filename=resume_doc["original_filename"],
        ats_result={
            "overall_score": ats.overall_score,
            "grade": ats.grade,
            "category_scores": ats.category_scores,
            "suggestions": ats.suggestions,
            "score_explanation": ats.score_explanation,
        },
        skills=skill_result.skills,
        sections=sections,
        job_description=job_description,
        job_match_result=job_match,
        llm_feedback=feedback,
    )
    result = mongo.db.analyses.insert_one(doc)
    doc["_id"] = result.inserted_id

    return jsonify({
        "analysis": public_analysis(doc),
        "skills_by_category": skill_result.skills_by_category,
        "llm_enabled": is_llm_enabled(),
    }), 201


@analysis_bp.route("/job-match", methods=["POST"])
@jwt_required()
def job_match():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    resume_id = data.get("resume_id") or ""
    job_description = (data.get("job_description") or "").strip()

    if not resume_id or not job_description:
        return jsonify({"error": "resume_id and job_description are required"}), 400

    oid = to_object_id(resume_id)
    if not oid:
        return jsonify({"error": "Invalid resume_id"}), 400

    resume_doc = mongo.db.resumes.find_one({"_id": oid, "user_id": user_id})
    if not resume_doc:
        return jsonify({"error": "Resume not found"}), 404

    text = resume_doc.get("extracted_text", "")
    if not text.strip():
        return jsonify({"error": "Resume has no extractable text"}), 422

    sim = compute_similarity(text, job_description)
    skill_result = extract_skills(text)

    # Extract job-description skills
    jd_skills = extract_skills(job_description)
    resume_skill_set = {s.lower() for s in skill_result.skills}
    jd_skill_set = {s.lower() for s in jd_skills.skills}

    matched_skills = [s for s in jd_skills.skills if s.lower() in resume_skill_set]
    missing_skills = [s for s in jd_skills.skills if s.lower() not in resume_skill_set]

    return jsonify({
        "tfidf_similarity": {
            "score": sim.score,
            "matched_keywords": sim.matched_keywords,
            "missing_keywords": sim.missing_keywords,
            "note": sim.note,
        },
        "skill_alignment": {
            "resume_skills": skill_result.skills,
            "jd_skills": jd_skills.skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "overlap_score": round(
                len(matched_skills) / len(jd_skills.skills) * 100, 1
            ) if jd_skills.skills else 0,
        }
    }), 200


@analysis_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    docs = list(mongo.db.analyses.find(
        {"user_id": user_id},
        {"extracted_text": 0}
    ).sort("created_at", -1).limit(50))
    return jsonify({"history": [public_analysis(d) for d in docs]}), 200


@analysis_bp.route("/<analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis(analysis_id):
    user_id = get_jwt_identity()
    oid = to_object_id(analysis_id)
    if not oid:
        return jsonify({"error": "Invalid analysis ID"}), 400
    doc = mongo.db.analyses.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Analysis not found"}), 404
    skill_result = extract_skills(
        mongo.db.resumes.find_one(
            {"_id": to_object_id(doc.get("resume_id", ""))}, {"extracted_text": 1}
        ).get("extracted_text", "") if doc.get("resume_id") else ""
    )
    return jsonify({
        "analysis": public_analysis(doc),
        "skills_by_category": skill_result.skills_by_category,
    }), 200


@analysis_bp.route("/<analysis_id>", methods=["DELETE"])
@jwt_required()
def delete_analysis(analysis_id):
    user_id = get_jwt_identity()
    oid = to_object_id(analysis_id)
    if not oid:
        return jsonify({"error": "Invalid analysis ID"}), 400
    result = mongo.db.analyses.delete_one({"_id": oid, "user_id": user_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Analysis not found"}), 404
    return jsonify({"message": "Analysis deleted"}), 200
