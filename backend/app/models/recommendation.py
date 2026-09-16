"""
Recommendation document schema helpers.
"""

from datetime import datetime, timezone


def create_recommendation_doc(
    user_id: str,
    analysis_id: str,
    roles: list,
    skill_gaps: list,
    learning_plan: list,
) -> dict:
    return {
        "user_id": user_id,
        "analysis_id": analysis_id,
        "roles": roles,
        "skill_gaps": skill_gaps,
        "learning_plan": learning_plan,
        "created_at": datetime.now(timezone.utc),
    }


def public_recommendation(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "analysis_id": doc.get("analysis_id"),
        "roles": doc.get("roles", []),
        "skill_gaps": doc.get("skill_gaps", []),
        "learning_plan": doc.get("learning_plan", []),
        "created_at": doc["created_at"].isoformat(),
    }
