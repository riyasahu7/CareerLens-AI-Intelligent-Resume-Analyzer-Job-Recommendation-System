from app.services.recommender import recommend_roles
from app.services.learning_plan import generate_learning_plan

def test_returns_all_roles():
    results = recommend_roles(["Python", "Flask", "PostgreSQL"])
    assert len(results) >= 7

def test_python_dev_scores_high():
    results = recommend_roles(["Python", "Flask", "REST API", "SQL", "Git", "Docker"])
    roles = {r.role: r for r in results}
    # All required skills matched — score should be well above 50
    assert roles["Python Developer"].match_score > 50

def test_empty_skills_all_low():
    results = recommend_roles([])
    for r in results:
        assert r.match_score == 0.0

def test_matched_skills_populated():
    results = recommend_roles(["React", "JavaScript", "HTML", "CSS", "Git"])
    roles = {r.role: r for r in results}
    assert "JavaScript" in roles["Frontend Developer"].matched_required

def test_learning_plan_not_empty():
    plan = generate_learning_plan(["Python", "SQL", "Docker"])
    assert len(plan) == 3
    assert plan[0]["skill"] in ["Python", "SQL", "Docker"]

def test_learning_plan_priority_sort():
    plan = generate_learning_plan(["Docker", "Python", "SQL"])
    priorities = [p["priority"] for p in plan]
    order = {"high": 0, "medium": 1, "low": 2}
    assert sorted(priorities, key=lambda x: order.get(x, 1)) == priorities

def test_learning_plan_unknown_skill():
    plan = generate_learning_plan(["QuantumFramework9000"])
    assert len(plan) == 1
    assert plan[0]["skill"] == "QuantumFramework9000"
    assert "beginner_explanation" in plan[0]
