from app.settings import settings
from fakes import fake_user, fake_credentials, FakeCredentials


class TestAuth(object):
    url: str

    def setup_class(self):
        self.url = '/authentication'

    def test_signup(self, client):
        payload = fake_user()

        response = client.post(url=f'{self.url}/signup', json=payload.model_dump())
        assert response.status_code == 201

        data = response.json()

        assert data.get('success') is True
        assert data.get('message') == 'User successfully created and a confirmation email has been sent via email.'

    def test_login(self, client, user):
        payload = FakeCredentials(email=user.email,password=settings.system_admin_default_password)
        response = client.post(url=f'{self.url}/signin', json=payload.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert 'user' in data

        user = data.get('user')

        assert 'access_token' in user
        assert user.get('access_token') is not None
        assert user.get('email') == payload.email
