from starlette.testclient import TestClient

from ._utils import get_bearer_header


class TestCommentRouter:
    def test_list_comments(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/comments', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert len(response.json()['data']) == 100

    def test_create_comment(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts?$top=1', headers=get_bearer_header(access_token)
        )
        post = response.json()['data'][0]

        response = test_client.post(
            '/comments',
            json={'body': 'This is a comment', 'postId': post['uid']},
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 201
        assert response.json()['body'] == 'This is a comment'

    def test_get_comment(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/comments', headers=get_bearer_header(access_token)
        )
        comment = response.json()['data'][0]

        response = test_client.get(
            f'/comments/{comment["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert response.json()['body'] == comment['body']

    def test_update_comment(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/comments', headers=get_bearer_header(access_token)
        )
        comment = response.json()['data'][0]

        response = test_client.put(
            f'/comments/{comment["uid"]}',
            json={'body': 'This is an updated comment'},
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 200
        assert response.json()['body'] == 'This is an updated comment'

    def test_delete_comment(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/comments', headers=get_bearer_header(access_token)
        )
        comment = response.json()['data'][0]

        response = test_client.delete(
            f'/comments/{comment["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 204

        response = test_client.get(
            f'/comments/{comment["uid"]}', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 404
