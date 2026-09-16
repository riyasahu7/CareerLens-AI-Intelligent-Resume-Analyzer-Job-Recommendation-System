import pytest
from app.services.ats_scorer import score_resume

FULL_RESUME = """
John Doe | john@example.com | +1 555 000 1234 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Experienced Python backend developer with 4 years building REST APIs.

EXPERIENCE
Backend Engineer at Acme Corp (2021-2024)
- Built microservices handling 1M requests/day
- Reduced latency by 40%

EDUCATION
B.Tech Computer Science, State University 2021

SKILLS
Python, Flask, PostgreSQL, Docker, AWS, Git, REST API

PROJECTS
Resume Analyser — built with Flask, MongoDB, React

CERTIFICATIONS
AWS Certified Developer
"""

def test_full_resume_high_score():
    skills = ["Python", "Flask", "PostgreSQL", "Docker", "AWS", "Git", "REST API"]
    r = score_resume(FULL_RESUME, skills)
    assert r.overall_score >= 60

def test_empty_resume_low_score():
    r = score_resume("", [])
    # Empty resume should score very low (< 10); formatting signals may contribute a tiny amount
    assert r.overall_score < 10

def test_grade_a():
    from app.services.ats_scorer import _grade
    assert _grade(90) == "A"

def test_grade_f():
    from app.services.ats_scorer import _grade
    assert _grade(30) == "F"

def test_suggestions_generated():
    r = score_resume("Name only resume text.", [])
    assert len(r.suggestions) > 0
