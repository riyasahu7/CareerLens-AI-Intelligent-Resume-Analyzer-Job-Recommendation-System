"""
ATS-style resume scoring engine.

Scoring methodology (clearly defined — we do not claim this matches any
proprietary ATS system):

  Category                  Weight
  ────────────────────────  ──────
  Section completeness       30 %
  Skill coverage             25 %
  Keyword match (if JD)      25 %   (redistributed to skills if no JD)
  Formatting signals         10 %
  Contact information        10 %

Each category returns a 0-100 sub-score; the weighted average becomes the
overall ATS score.

When no job description is provided the keyword-match weight (25 %) is
split equally to section completeness and skill coverage.
"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Section detection patterns                                           #
# ------------------------------------------------------------------ #

SECTION_PATTERNS: dict[str, list[str]] = {
    "contact": [
        r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",           # email
        r"\+?[\d\s\-\(\)]{7,}",                        # phone
        r"linkedin\.com/in/",                           # LinkedIn
        r"github\.com/",                                # GitHub
    ],
    "summary": [
        r"\b(summary|profile|objective|about me|career objective|professional summary)\b",
    ],
    "experience": [
        r"\b(experience|work history|employment|professional experience|internship|intern)\b",
    ],
    "education": [
        r"\b(education|academic|degree|bachelor|master|phd|b\.?tech|m\.?tech|b\.?sc|m\.?sc|university|college|gpa)\b",
    ],
    "skills": [
        r"\b(skills|technical skills|core competencies|technologies|stack)\b",
    ],
    "projects": [
        r"\b(projects|personal projects|academic projects|portfolio)\b",
    ],
    "certifications": [
        r"\b(certifications?|certificates?|certified|licensure|credential)\b",
    ],
    "achievements": [
        r"\b(achievements?|awards?|honours?|honors?|accomplishments?|recognition)\b",
    ],
}

# Points allocated per section (used for completeness score)
SECTION_WEIGHTS = {
    "contact":        20,
    "summary":        10,
    "experience":     20,
    "education":      15,
    "skills":         15,
    "projects":       10,
    "certifications":  5,
    "achievements":    5,
}


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

@dataclass
class ATSResult:
    overall_score: float = 0.0
    grade: str = ""
    category_scores: dict = field(default_factory=dict)
    sections_found: dict = field(default_factory=dict)
    formatting_signals: dict = field(default_factory=dict)
    contact_info: dict = field(default_factory=dict)
    suggestions: list = field(default_factory=list)
    score_explanation: str = (
        "Score is based on section completeness, skill coverage, "
        "formatting signals, and contact information presence. "
        "It does not predict hiring outcomes."
    )


def score_resume(
    resume_text: str,
    detected_skills: list[str],
    job_description: str | None = None,
    job_keywords: list[str] | None = None,
) -> ATSResult:
    """
    Score a resume and return a detailed ATSResult.

    Args:
        resume_text:      Raw text extracted from the resume.
        detected_skills:  Skills already extracted by skill_extractor.
        job_description:  Optional JD text for keyword matching.
        job_keywords:     Optional pre-extracted JD keywords.
    """
    text_lower = resume_text.lower()

    # ── 1. Section completeness ──────────────────────────────────────
    sections_found, section_score = _score_sections(text_lower)

    # ── 2. Contact information ───────────────────────────────────────
    contact_info, contact_score = _score_contact(resume_text)

    # ── 3. Skill coverage ────────────────────────────────────────────
    skill_score = min(100.0, len(detected_skills) * 5.0)  # +5 per skill, cap 100

    # ── 4. Keyword match (only when JD provided) ─────────────────────
    matched_kw: list[str] = []
    missing_kw: list[str] = []
    keyword_score = 0.0

    if job_description and job_keywords:
        for kw in job_keywords:
            if kw.lower() in text_lower:
                matched_kw.append(kw)
            else:
                missing_kw.append(kw)
        total_kw = len(job_keywords)
        keyword_score = (len(matched_kw) / total_kw * 100) if total_kw else 0.0

    # ── 5. Formatting signals ─────────────────────────────────────────
    formatting_signals, formatting_score = _score_formatting(resume_text)

    # ── 6. Weighted overall score ─────────────────────────────────────
    if job_keywords:
        # With JD: use keyword_match weight
        overall = (
            section_score   * 0.30 +
            skill_score     * 0.25 +
            keyword_score   * 0.25 +
            formatting_score * 0.10 +
            contact_score   * 0.10
        )
    else:
        # Without JD: redistribute keyword weight to sections/skills
        overall = (
            section_score   * 0.425 +
            skill_score     * 0.375 +
            formatting_score * 0.10 +
            contact_score   * 0.10
        )

    overall = round(min(100.0, overall), 1)

    # ── 7. Grade ──────────────────────────────────────────────────────
    grade = _grade(overall)

    # ── 8. Suggestions ───────────────────────────────────────────────
    suggestions = _build_suggestions(
        sections_found, contact_info, detected_skills,
        formatting_signals, missing_kw
    )

    category_scores = {
        "section_completeness": round(section_score, 1),
        "skill_coverage":       round(skill_score, 1),
        "contact_information":  round(contact_score, 1),
        "formatting":           round(formatting_score, 1),
    }
    if job_keywords:
        category_scores["keyword_match"] = round(keyword_score, 1)

    return ATSResult(
        overall_score=overall,
        grade=grade,
        category_scores=category_scores,
        sections_found=sections_found,
        formatting_signals=formatting_signals,
        contact_info=contact_info,
        suggestions=suggestions,
    )


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def detect_sections(text: str) -> dict[str, bool]:
    """Public helper — also used by the analysis blueprint."""
    found, _ = _score_sections(text.lower())
    return found


def _score_sections(text_lower: str) -> tuple[dict, float]:
    found: dict[str, bool] = {}
    earned = 0
    total_weight = sum(SECTION_WEIGHTS.values())

    for section, patterns in SECTION_PATTERNS.items():
        detected = any(re.search(p, text_lower) for p in patterns)
        found[section] = detected
        if detected:
            earned += SECTION_WEIGHTS[section]

    score = (earned / total_weight) * 100
    return found, score


def _score_contact(text: str) -> tuple[dict, float]:
    info: dict[str, bool] = {}

    email_match = re.search(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", text, re.I)
    phone_match = re.search(r"\+?[\d\s\-\(\)]{7,15}", text)
    linkedin_match = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    github_match = re.search(r"github\.com/[\w\-]+", text, re.I)

    info["email"] = bool(email_match)
    info["phone"] = bool(phone_match)
    info["linkedin"] = bool(linkedin_match)
    info["github"] = bool(github_match)

    # Weighted: email+phone critical (35 each), linkedin (20), github (10)
    score = (
        35 * info["email"] +
        35 * info["phone"] +
        20 * info["linkedin"] +
        10 * info["github"]
    )
    return info, min(100.0, float(score))


def _score_formatting(text: str) -> tuple[dict, float]:
    signals: dict[str, bool] = {}

    word_count = len(text.split())
    signals["adequate_length"] = 200 <= word_count <= 1200
    signals["not_too_short"] = word_count >= 150
    signals["not_too_long"] = word_count <= 1500
    signals["has_bullet_points"] = bool(re.search(r"^[\•\-\*\u2022\u2023]\s", text, re.M))
    signals["has_consistent_dates"] = bool(
        re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", text, re.I)
        or re.search(r"\b(20\d{2}|19\d{2})\b", text)
    )
    signals["no_obvious_tables"] = "| --- |" not in text and "colspan" not in text.lower()

    score = sum(signals.values()) / len(signals) * 100
    return signals, round(score, 1)


def _grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _build_suggestions(
    sections: dict,
    contact: dict,
    skills: list,
    formatting: dict,
    missing_kw: list,
) -> list[dict]:
    suggestions = []

    if not contact.get("email"):
        suggestions.append({
            "type": "contact",
            "priority": "high",
            "message": "Add a professional email address to your resume.",
        })
    if not contact.get("phone"):
        suggestions.append({
            "type": "contact",
            "priority": "high",
            "message": "Include a contact phone number.",
        })
    if not contact.get("linkedin"):
        suggestions.append({
            "type": "contact",
            "priority": "medium",
            "message": "Add your LinkedIn profile URL to increase professional visibility.",
        })
    if not sections.get("summary"):
        suggestions.append({
            "type": "section",
            "priority": "high",
            "message": "Add a professional summary or profile section near the top of your resume.",
        })
    if not sections.get("experience"):
        suggestions.append({
            "type": "section",
            "priority": "high",
            "message": "Include a work experience or internship section.",
        })
    if not sections.get("projects"):
        suggestions.append({
            "type": "section",
            "priority": "medium",
            "message": "Add a projects section to showcase practical experience.",
        })
    if not sections.get("certifications"):
        suggestions.append({
            "type": "section",
            "priority": "low",
            "message": "Consider adding certifications to validate your skills.",
        })
    if len(skills) < 5:
        suggestions.append({
            "type": "skills",
            "priority": "high",
            "message": "Your skills section appears sparse. List specific technical and soft skills.",
        })
    if not formatting.get("has_bullet_points"):
        suggestions.append({
            "type": "formatting",
            "priority": "medium",
            "message": "Use bullet points to improve readability of experience and projects.",
        })
    if not formatting.get("adequate_length"):
        suggestions.append({
            "type": "formatting",
            "priority": "medium",
            "message": "Aim for 300–800 words. Very short resumes may appear incomplete; very long ones may not be read fully.",
        })
    if missing_kw:
        top_missing = missing_kw[:5]
        suggestions.append({
            "type": "keywords",
            "priority": "high",
            "message": f"Consider incorporating these job-relevant keywords: {', '.join(top_missing)}.",
        })

    return suggestions
