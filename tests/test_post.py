from starlette.testclient import TestClient

from ._utils import get_bearer_header


class TestPostRouter:
    def test_list_posts(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert len(response.json()['data']) == 100

    def test_create_post(self, test_client: TestClient, access_token: str):
        response = test_client.post(
            '/posts',
            json={
                'title': 'This is a post',
                'body': 'This is a post',
                'tags': ['tag1', 'tag2'],
            },
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 201
        assert response.json()['body'] == 'This is a post'

    def test_get_post(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts', headers=get_bearer_header(access_token)
        )
        post = response.json()['data'][0]

        response = test_client.get(
            f'/posts/{post["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert response.json()['body'] == post['body']

    def test_update_post(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts', headers=get_bearer_header(access_token)
        )
        post = response.json()['data'][0]

        response = test_client.put(
            f'/posts/{post["uid"]}',
            json={
                'title': 'This is an updated post',
                'body': 'This is an updated post',
                'tags': ['tag1', 'tag2'],
            },
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 200
        assert response.json()['body'] == 'This is an updated post'

    def test_delete_post(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts', headers=get_bearer_header(access_token)
        )
        post = response.json()['data'][0]

        response = test_client.delete(
            f'/posts/{post["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 204

        response = test_client.get(
            f'/posts/{post["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 404
