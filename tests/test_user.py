def test_user_registration(test_client):
    response = test_client.post(
        "/register/",
        json={
            "username": "user",
            "password": "some_password",
            "email": "some_email@gmail.com",
            "full_name": "user_user1",
            "second_name": "user1"
        }
    )
    json_response = response.json()
    assert response.status_code == 201
    assert "id" in json_response
    assert "username" in json_response
    assert "password" not in json_response
    assert "email" in json_response


def test_user_valid_registration(test_client):
    response = test_client.post(
        "/register/",
        json={
            "username": "user2",
            "password": "some_password2",
            "email": "some_email2@gmail.com",
            "full_name": "user_user2",
            "second_name": "user2"
        }
    )
    json_response = response.json()
    assert response.status_code == 201
    assert json_response["username"] == "user2"
    assert "password" not in json_response
    assert json_response["email"] == "some_email2@gmail.com"
    assert json_response["full_name"] == "user_user2"
    assert json_response["second_name"] == "user2"


def test_user_invalid_registration(test_client):
    response = test_client.post(
        "/register/",
        json={
            "username": "Al",
            "password": "123",
            "email": "alice_gmail.com",
            "full_name": "Alice Dilan",
            "second_name": "Dilan"
        }
    )
    assert response.status_code == 422


def test_duplicate_user(test_client):
    response = test_client.post(
        "/register/",
        json={
            "username": "Bob",
            "password": "12345",
            "email": "bob@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan"
        }
    )
    json_response = response.json()
    assert response.status_code == 400
    assert json_response["detail"] == "User already exist"
    assert "password" not in json_response


def test_user_valid_login(test_client):
    response = test_client.post(
        "/register/login/",
        json={
            "username": "Bob",
            "password": "12345",
            "email": "bob@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan"
        }
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_user_invalid_login(test_client):
    response = test_client.post(
        "/register/login/",
        json={
            "username": "Bob3",
            "password": "12345",
            "email": "bob3@gmail.com",
            "full_name": "Bob Dilan",
            "second_name": "Dilan"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_user(test_client):
    response = test_client.get("/register/1")

    assert response.status_code == 200
    assert "username" in response.json()


def test_user_not_found(test_client):
    response = test_client.get("/register/10")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_list(test_client):
    response = test_client.get("/register/")

    assert response.status_code == 200
    assert not response.json() == []
