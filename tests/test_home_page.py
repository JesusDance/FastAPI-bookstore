def test_home_page(test_client):
    response = test_client.get("/")
    json_data = response.json()

    assert response.status_code == 200
    assert "message" in json_data
    assert json_data["message"] == "Hello from FastAPI!"