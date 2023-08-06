from fakes import fake_user, fake_credentials


class TestAuthentication(object):
    url: str

    def setup_class(self):
        self.url = '/authentication'

    def test_signup(self, client):
        payload = fake_user()

        response = client.post(url=f'{self.url}/signup', json=payload)
        assert response.status_code == 200

        data = response.json()

        assert data.get('success') is True
        assert data.get('message') == 'Account successfully created and confirmation has been sent via email'


    def test_login(self, client):
        payload = fake_credentials()
        response = client.post(url=f'{self.url}/signin')