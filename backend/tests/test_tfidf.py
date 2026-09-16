import pytest
from app.services.tfidf_service import compute_similarity

def test_identical_docs_score_high():
    text = "Python developer with Flask REST API and PostgreSQL experience."
    r = compute_similarity(text, text)
    assert r.score > 90

def test_unrelated_docs_score_low():
    resume = "Python machine learning data science pandas numpy."
    jd = "Graphic designer Photoshop Illustrator brand identity visual."
    r = compute_similarity(resume, jd)
    assert r.score < 30

def test_empty_inputs():
    r = compute_similarity("", "some job description")
    assert r.score == 0.0

def test_matched_keywords_present():
    resume = "Python Flask REST API Docker AWS PostgreSQL"
    jd = "We need Python Flask REST API experience and Docker knowledge."
    r = compute_similarity(resume, jd)
    assert len(r.matched_keywords) > 0
