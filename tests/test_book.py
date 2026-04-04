def test_create_book(test_client, default_user_token):
    response = test_client.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "test_book",
            "author": "test_author",
            "price": 40,
            "description": "some_description",
            "in_stock": True,
        },
    )
    json_response = response.json()
    assert response.status_code == 201
    assert "title" in json_response
    assert "author" in json_response
    assert "price" in json_response
    assert "description" in json_response
    assert "in_stock" in json_response


def test_create_valid_book(test_client, default_user_token):
    response = test_client.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "test_book",
            "author": "test_author",
            "price": 30.5,
            "description": "some_description",
            "in_stock": False,
        },
    )
    json_response = response.json()
    assert response.status_code == 201
    assert json_response["title"] == "test_book"
    assert json_response["author"] == "test_author"
    assert json_response["price"] == 30.5
    assert json_response["description"] == "some_description"
    assert json_response["in_stock"] == False


def test_create_invalid_book(test_client, default_user_token):
    response = test_client.post(
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


def test_get_no_book(test_client, default_user_token):
    response = test_client.get(
        "/bookstore/6", headers={"Authorization": "Bearer " + default_user_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_no_access_to_book(test_client, second_user_token):
    response = test_client.get(
        "/bookstore/1", headers={"Authorization": "Bearer " + second_user_token}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "You don't have access for this book"


def test_book_flow(test_client, default_user_token):
    response_list = test_client.get(
        "/bookstore/", headers={"Authorization": "Bearer " + default_user_token}
    )
    assert response_list.status_code == 200
    assert not response_list.json() == []

    response = test_client.post(
        "/bookstore/",
        headers={"Authorization": "Bearer " + default_user_token},
        json={
            "title": "test_book",
            "author": "test_author",
            "price": 30.5,
            "description": "some_description",
            "in_stock": False,
        },
    )
    assert response.status_code == 201

    response_get = test_client.get(
        "/bookstore/3", headers={"Authorization": "Bearer " + default_user_token}
    )
    assert response_get.status_code == 200
    assert response_get.json()["title"] == "Story"

    response_patch = test_client.patch(
        "/bookstore/3",
        headers={"Authorization": "Bearer " + default_user_token},
        json={"title": "Story2"},
    )
    assert response_patch.status_code == 200
    assert response_patch.json()["title"] == "Story2"

    response_delete = test_client.delete(
        "/bookstore/4", headers={"Authorization": "Bearer " + default_user_token}
    )
    assert response_delete.status_code == 200
    assert response_delete.json()["message"] == "Book deleted successfully"
