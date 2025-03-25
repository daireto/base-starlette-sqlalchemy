from starlette.testclient import TestClient

from ._utils import get_bearer_header


class TestUserRouter:
    def test_list_users(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/users', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert len(response.json()['data']) == 100

    def test_create_user(self, test_client: TestClient, access_token: str):
        with open('tests/data/user_create.json', 'r') as f:
            data = f.read()

        response = test_client.post(
            '/users', content=data, headers=get_bearer_header(access_token)
        )
        assert response.status_code == 201
        assert response.json()['username'] == 'daireto'

    def test_get_user(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/users', headers=get_bearer_header(access_token)
        )
        user = response.json()['data'][0]

        response = test_client.get(
            f'/users/{user["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert response.json()['username'] == user['username']

    def test_update_user(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/users/daireto15', headers=get_bearer_header(access_token)
        )
        user = response.json()

        with open('tests/data/user_update.json', 'r') as f:
            data = f.read()

        response = test_client.put(
            f'/users/{user["uid"]}',
            content=data,
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'daireto15'

    def test_delete_user(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/users', headers=get_bearer_header(access_token)
        )
        user = response.json()['data'][0]

        response = test_client.delete(
            f'/users/{user["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 204

        response = test_client.get(
            f'/users/{user["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 404
