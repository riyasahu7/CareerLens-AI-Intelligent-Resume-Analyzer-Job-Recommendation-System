"""
LLM integration service abstraction.

Design principle:
  - If OPENAI_API_KEY is set in the environment, use OpenAI's API.
  - If not, fall back to rule-based feedback.  The fallback is clearly
    labelled so the UI can display "Rule-based suggestions" rather than
    claiming AI generated the output.
  - Never expose the API key in responses or logs.
  - All prompts and responses are structured JSON where possible.

The service is intentionally isolated so it can be swapped for another
provider (Anthropic, Google, local Ollama) by editing only this file.
"""

import logging
import json
import re
from flask import current_app

logger = logging.getLogger(__name__)


def is_llm_enabled() -> bool:
    """Return True if an LLM API key is configured."""
    try:
        return bool(current_app.config.get("LLM_ENABLED", False))
    except RuntimeError:
        # Outside app context
        import os
        return bool(os.environ.get("OPENAI_API_KEY", ""))


def get_resume_feedback(resume_text: str, job_description: str | None = None) -> dict:
    """
    Generate structured resume feedback.

    Returns:
        {
            "source": "llm" | "rule_based",
            "suggestions": [...],
            "overall_impression": str,
            "key_strengths": [...],
            "areas_for_improvement": [...],
        }
    """
    if is_llm_enabled():
        try:
            return _llm_feedback(resume_text, job_description)
        except Exception as exc:
            logger.warning("LLM call failed (%s); falling back to rule-based", exc)

    return _rule_based_feedback(resume_text, job_description)


# ------------------------------------------------------------------ #
# LLM path                                                             #
# ------------------------------------------------------------------ #

def _llm_feedback(resume_text: str, job_description: str | None) -> dict:
    """Call OpenAI ChatCompletion and parse structured JSON response."""
    import openai  # type: ignore

    openai.api_key = current_app.config["OPENAI_API_KEY"]
    model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = (
        "You are a professional career coach reviewing a resume. "
        "Provide honest, specific, and actionable feedback. "
        "Do NOT invent education, experience, skills, or achievements that are not present. "
        "Return ONLY valid JSON in the following structure:\n"
        "{\n"
        '  "overall_impression": "string",\n'
        '  "key_strengths": ["string", ...],\n'
        '  "areas_for_improvement": ["string", ...],\n'
        '  "suggestions": [\n'
        '    {"section": "string", "issue": "string", "recommendation": "string"}\n'
        "  ]\n"
        "}"
    )

    user_content = f"RESUME:\n{resume_text[:4000]}"
    if job_description:
        user_content += f"\n\nJOB DESCRIPTION:\n{job_description[:2000]}"

    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        max_tokens=1200,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    parsed = json.loads(raw)
    parsed["source"] = "llm"
    return parsed


# ------------------------------------------------------------------ #
# Rule-based fallback                                                  #
# ------------------------------------------------------------------ #

def _rule_based_feedback(resume_text: str, job_description: str | None) -> dict:
    """
    Deterministic rule-based feedback.
    Clearly labelled as rule-based — not presented as AI-generated.
    """
    text_lower = resume_text.lower()
    suggestions = []

    # Check for quantified achievements
    has_numbers = bool(re.search(r"\b\d+\s*(%|percent|users|customers|projects|services|ms|seconds|hours|days|million|k\b)", text_lower))
    if not has_numbers:
        suggestions.append({
            "section": "Experience",
            "issue": "Achievements lack quantification.",
            "recommendation": (
                "Where possible, add numbers to demonstrate impact. "
                "For example: 'Improved API response time by 30%' or "
                "'Managed a team of 4 engineers'."
            ),
        })

    # Check for weak verbs
    weak_verbs = ["helped", "worked on", "was responsible for", "assisted", "did"]
    found_weak = [v for v in weak_verbs if v in text_lower]
    if found_weak:
        suggestions.append({
            "section": "Experience",
            "issue": f"Weak action verbs detected: {', '.join(found_weak)}.",
            "recommendation": (
                "Replace with strong action verbs such as: Built, Designed, "
                "Implemented, Optimised, Led, Delivered, Automated."
            ),
        })

    # Summary check
    if not re.search(r"\b(summary|profile|objective|about)\b", text_lower):
        suggestions.append({
            "section": "Summary",
            "issue": "No professional summary detected.",
            "recommendation": (
                "Add a 2–4 sentence professional summary at the top that "
                "highlights your experience level, core skills, and career goal."
            ),
        })

    # Skills section
    if not re.search(r"\bskills\b", text_lower):
        suggestions.append({
            "section": "Skills",
            "issue": "No dedicated skills section found.",
            "recommendation": "Add a skills section listing your technical and soft skills.",
        })

    # LinkedIn presence
    if "linkedin.com" not in text_lower:
        suggestions.append({
            "section": "Contact",
            "issue": "LinkedIn URL not present.",
            "recommendation": "Add your LinkedIn profile URL. Recruiters frequently check it.",
        })

    # Projects
    if not re.search(r"\bproject", text_lower):
        suggestions.append({
            "section": "Projects",
            "issue": "No projects section detected.",
            "recommendation": (
                "Include 2–3 projects with brief descriptions, technologies used, "
                "and links to GitHub or a live demo."
            ),
        })

    # Determine key strengths based on what is present
    key_strengths = []
    if re.search(r"\b(led|managed|coordinated)\b", text_lower):
        key_strengths.append("Demonstrates leadership or team coordination experience.")
    if has_numbers:
        key_strengths.append("Resume includes quantified achievements.")
    if re.search(r"\bgithub\.com\b", text_lower):
        key_strengths.append("GitHub presence signals active coding practice.")
    if re.search(r"\b(certif|certified)\b", text_lower):
        key_strengths.append("Certifications demonstrate commitment to learning.")
    if not key_strengths:
        key_strengths.append("Resume text was extracted successfully for analysis.")

    areas = [s["issue"] for s in suggestions[:3]]

    return {
        "source": "rule_based",
        "overall_impression": (
            "Analysis is based on structural rules applied to your resume text. "
            "For deeper narrative feedback, configure an LLM provider."
        ),
        "key_strengths": key_strengths,
        "areas_for_improvement": areas,
        "suggestions": suggestions,
    }
