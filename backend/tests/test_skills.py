import pytest
from app.services.skill_extractor import extract_skills

def test_detects_python():
    r = extract_skills("I have 3 years of Python experience.")
    assert "Python" in r.skills

def test_detects_react():
    r = extract_skills("Built a frontend app using React and TypeScript.")
    assert "React" in r.skills
    assert "TypeScript" in r.skills

def test_no_false_positive_c():
    r = extract_skills("I love cooking and swimming.")
    assert "C" not in r.skills

def test_empty_text():
    r = extract_skills("")
    assert r.skills == []
    assert r.total_count == 0

def test_category_grouping():
    r = extract_skills("Python, Flask, PostgreSQL, Docker, AWS")
    assert r.skills_by_category != {}
    assert r.total_count >= 4

def test_case_insensitive():
    r = extract_skills("PYTHON DJANGO REACT")
    assert "Python" in r.skills
