import pytest
from starlette.testclient import TestClient

from app.main import app
from app.settings import settings
from fakes import fake_credentials


@pytest.fixture(scope='session')
def client():
    test_client = TestClient(app)

    return test_client


@pytest.fixture(scope='session')
def auth_client(client):
    credentials = fake_credentials()
    response = client.post('/authentication/login', json=credentials.model_dump())
    assert response.status_code == 200

    data = response.json()

    assert 'access_token' in data
    test_client = TestClient(app, headers={
        "Authorization": f"Bearer {data.get('access_token')}"
    })

    return test_client


@pytest.fixture(scope='session')
def repo():
    return settings.get_repo()
