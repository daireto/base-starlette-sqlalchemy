import pytest
from starlette.testclient import TestClient

from core.settings import Settings
from main import app


@pytest.fixture(scope='module')
def test_client():
    with TestClient(app) as client:
        Settings.database.DATABASE_URL = 'sqlite+aiosqlite://'
        yield client


@pytest.fixture(scope='module')
def access_token(test_client: TestClient):
    with open('tests/data/login.json', 'r') as f:
        login_data = f.read()

    response = test_client.post('/auth/login', content=login_data)
    assert response.status_code == 200

    return response.json()['accessToken']
