import os

os.environ["DATABASE_URL"] = "sqlite:///./test_secure_upi.db"
os.environ["SECRET_KEY"] = "test-secret-at-least-thirty-two-bytes-long"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
