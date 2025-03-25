from starlette.testclient import TestClient

from ._utils import get_bearer_header


class TestReactionRouter:
    def test_list_post_reactions(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/posts', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert len(response.json()['data']) == 100

    def test_list_comment_reactions(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/comments', headers=get_bearer_header(access_token)
        )
        assert response.status_code == 200
        assert len(response.json()['data']) == 100

    def test_create_post_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/posts?$top=1', headers=get_bearer_header(access_token)
        )
        post = response.json()['data'][0]

        response = test_client.post(
            '/reactions',
            json={
                'reactionType': 'LIKE',
                'targetId': post['uid'],
                'targetType': 'post',
            },
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 201
        assert response.json()['reactionType'] == 'LIKE'

    def test_create_comment_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/comments?$top=1', headers=get_bearer_header(access_token)
        )
        comment = response.json()['data'][0]

        response = test_client.post(
            '/reactions',
            json={
                'reactionType': 'LIKE',
                'targetId': comment['uid'],
                'targetType': 'comment',
            },
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 201
        assert response.json()['reactionType'] == 'LIKE'

    def test_get_post_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/posts?$top=1', headers=get_bearer_header(access_token)
        )
        reaction = response.json()['data'][0]

        response = test_client.get(
            f'/reactions/posts/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 200
        assert response.json()['uid'] == reaction['uid']

    def test_get_comment_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/comments?$top=1', headers=get_bearer_header(access_token)
        )
        reaction = response.json()['data'][0]

        response = test_client.get(
            f'/reactions/comments/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 200
        assert response.json()['uid'] == reaction['uid']

    def test_delete_post_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/posts?$top=1', headers=get_bearer_header(access_token)
        )
        reaction = response.json()['data'][0]

        response = test_client.delete(
            f'/reactions/posts/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 204

        response = test_client.get(
            f'/reactions/posts/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 404

    def test_delete_comment_reaction(self, test_client: TestClient, access_token: str):
        response = test_client.get(
            '/reactions/comments?$top=1', headers=get_bearer_header(access_token)
        )
        reaction = response.json()['data'][0]

        response = test_client.delete(
            f'/reactions/comments/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 204

        response = test_client.get(
            f'/reactions/comments/{reaction["uid"]}',
            headers=get_bearer_header(access_token),
        )
        assert response.status_code == 404
