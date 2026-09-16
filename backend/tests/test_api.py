import pytest
from app import create_app

TEST_CONFIG = {
    "TESTING": True,
    "MONGO_URI": "mongodb://localhost:27017/careerlens_test",
    "JWT_SECRET_KEY": "test-secret",
    "SECRET_KEY": "test-secret",
    "WTF_CSRF_ENABLED": False,
}

@pytest.fixture
def client():
    app = create_app(TEST_CONFIG)
    with app.test_client() as c:
        yield c

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code in (200, 503)  # 503 if no local mongo
    data = r.get_json()
    assert "status" in data

def test_register_missing_fields(client):
    r = client.post("/api/auth/register", json={})
    assert r.status_code == 400

def test_register_bad_email(client):
    r = client.post("/api/auth/register", json={
        "email": "notanemail", "password": "Pass1234", "full_name": "Test"
    })
    assert r.status_code == 400

def test_login_wrong_credentials(client):
    r = client.post("/api/auth/login", json={
        "email": "nobody@example.com", "password": "wrongpass"
    })
    assert r.status_code == 401

def test_protected_route_no_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401

def test_upload_no_file(client):
    # Need auth token — just check 401 without token
    r = client.post("/api/resumes")
    assert r.status_code == 401
