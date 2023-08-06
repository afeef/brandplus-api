def test_healthy(client):
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {"message": "Healthy!"}
