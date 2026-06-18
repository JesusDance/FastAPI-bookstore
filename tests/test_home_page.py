import pytest


@pytest.mark.asyncio
async def test_home_page(test_client_api):
    response = await test_client_api.get("/", auth=("admin", "admin_pass"))
    json_data = response.json()

    assert response.status_code == 200
    assert "message" in json_data
    assert json_data["message"] == "Hello admin"
