from starlette.testclient import TestClient


class TestAuthRouter:
    def test_login(self, test_client: TestClient):
        with open('tests/data/login.json', 'r') as f:
            login_data = f.read()

        response = test_client.post('/auth/login', content=login_data)
        assert response.status_code == 200
        assert 'accessToken' in response.json()

    def test_login_incorrect_credentials(self, test_client: TestClient):
        with open('tests/data/login_incorrect_credentials.json', 'r') as f:
            login_data = f.read()

        response = test_client.post('/auth/login', content=login_data)
        assert response.status_code == 401
        assert 'message' in response.json()

    def test_signup(self, test_client: TestClient):
        with open('tests/data/signup.json', 'r') as f:
            signup_data = f.read()

        response = test_client.post('/auth/signup', content=signup_data)
        assert response.status_code == 201
        assert 'accessToken' in response.json()

    def test_signup_user_already_exists(self, test_client: TestClient):
        with open('tests/data/signup_user_already_exists.json', 'r') as f:
            signup_data = f.read()

        response = test_client.post('/auth/signup', content=signup_data)
        assert response.status_code == 400
        assert 'message' in response.json()

    def test_signup_passwords_mismatch(self, test_client: TestClient):
        with open('tests/data/signup_passwords_mismatch.json', 'r') as f:
            signup_data = f.read()

        response = test_client.post('/auth/signup', content=signup_data)
        assert response.status_code == 400
        assert 'message' in response.json()
