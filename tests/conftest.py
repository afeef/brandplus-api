import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture(scope='session')
def client():
    test_client = TestClient(app)

    return test_client
