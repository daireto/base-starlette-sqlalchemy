from starlette.testclient import TestClient

from ._utils import get_bearer_header


class TestAccountRouter:
    def test_get_current_user(
        self, test_client: TestClient, access_token: str
    ):
        response = test_client.get(
            '/users/me', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'daireto15'

    def test_update_current_user(
        self, test_client: TestClient, access_token: str
    ):
        with open('tests/data/user_update.json', 'r') as f:
            data = f.read()

        response = test_client.put(
            '/users/me', content=data, headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'daireto15'
        assert response.json()['email'] == 'daireto@yopmail.com'

    def test_delete_current_user(
        self, test_client: TestClient, access_token: str
    ):
        response = test_client.delete(
            '/users/me', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 204

        response = test_client.get(
            '/users/me', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 404
