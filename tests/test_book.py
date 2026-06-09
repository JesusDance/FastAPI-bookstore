import pytest


@pytest.mark.asyncio
async def test_create_book(test_client_api, default_user_token):
    response = await test_client_api.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "test_book",
            "price": 30.5,
            "description": "some_description",
            "in_stock": True,
        },
    )
    json_response = response.json()
    assert response.status_code == 201
    assert json_response["title"] == "test_book"
    assert json_response["author"] == "test_author"
    assert json_response["price"] == 30.5
    assert json_response["description"] == "some_description"
    assert json_response["in_stock"] == True


@pytest.mark.asyncio
async def test_create_duplicate_book(test_client_api, default_user_token):
    response = await test_client_api.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "test_book",
            "price": 30.5,
            "description": "some_description",
            "in_stock": False,
        },
    )
    json_response = response.json()
    assert response.status_code == 409
    assert json_response["detail"] == "Book already exists"


@pytest.mark.asyncio
async def test_create_invalid_book(test_client, default_user_token):
    response = await test_client.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "",
            "author": "te",
            "price": 55,
            "description": "some_description",
            "in_stock": "False",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_no_book(test_client, default_user_token):
    response = await test_client.get(
        "/bookstore/999", headers={"Authorization": "Bearer " + default_user_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


@pytest.mark.asyncio
async def test_no_access_to_book(test_client, second_user_token):
    response = await test_client.get(
        "/bookstore/1", headers={"Authorization": "Bearer " + second_user_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "You don't have access for this book"


@pytest.mark.asyncio
async def test_book_flow(test_client_api, second_user_token): #Інтеграційний тест
    response_list = await test_client_api.get(
        "/bookstore/", headers={"Authorization": "Bearer " + second_user_token}
    )
    assert response_list.status_code == 200
    assert not response_list.json() == []

    response = await test_client_api.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + second_user_token},
        json={
            "title": "test_book",
            "author": "test_author",
            "price": 30.5,
            "description": "some_description",
            "in_stock": False,
        },
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    response_get = await test_client_api.get(
        f"/bookstore/{book_id}", headers={"Authorization": "Bearer " + second_user_token}
    )
    assert response_get.status_code == 200
    assert response_get.json()["title"] == "test_book"

    response_patch = await test_client_api.patch(
        f"/bookstore/{book_id}",
        headers={"Authorization": "Bearer " + second_user_token},
        json={"title": "Story2"},
    )
    assert response_patch.status_code == 200
    assert response_patch.json()["title"] == "Story2"

    response_delete = await test_client_api.delete(
        f"/bookstore/{book_id}", headers={"Authorization": "Bearer " + second_user_token}
    )
    assert response_delete.status_code == 200
    assert response_delete.json()["message"] == "Book deleted successfully"
