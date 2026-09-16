"""
Analysis document schema helpers.
"""

from datetime import datetime, timezone


def create_analysis_doc(
    user_id: str,
    resume_id: str,
    resume_filename: str,
    ats_result: dict,
    skills: list,
    sections: dict,
    job_description: str | None = None,
    job_match_result: dict | None = None,
    llm_feedback: dict | None = None,
) -> dict:
    return {
        "user_id": user_id,
        "resume_id": resume_id,
        "resume_filename": resume_filename,
        "ats_result": ats_result,
        "skills": skills,
        "sections": sections,
        "job_description": job_description,
        "job_match_result": job_match_result,
        "llm_feedback": llm_feedback,
        "created_at": datetime.now(timezone.utc),
    }


def public_analysis(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "resume_id": doc.get("resume_id"),
        "resume_filename": doc.get("resume_filename", ""),
        "ats_result": doc.get("ats_result", {}),
        "skills": doc.get("skills", []),
        "sections": doc.get("sections", {}),
        "job_description_provided": bool(doc.get("job_description")),
        "job_match_result": doc.get("job_match_result"),
        "llm_feedback": doc.get("llm_feedback"),
        "created_at": doc["created_at"].isoformat(),
    }
