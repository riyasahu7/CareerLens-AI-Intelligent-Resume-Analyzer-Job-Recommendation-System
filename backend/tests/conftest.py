"""
Shared pytest fixtures.
"""
import pytest
from app import create_app

TEST_CONFIG = {
    "TESTING": True,
    "MONGO_URI": "mongodb://localhost:27017/careerlens_test",
    "JWT_SECRET_KEY": "test-secret",
    "SECRET_KEY": "test-secret",
}

@pytest.fixture(scope="session")
def app():
    return create_app(TEST_CONFIG)

@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c
