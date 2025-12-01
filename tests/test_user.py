import pytest
from unittest.mock import AsyncMock
from fastapi import status

# --- User Router Tests ---

def test_checkemail_available(client, mock_user_crud):
    mock_user_crud.get_user_by_email.return_value = None
    response = client.get("/api/v1/users/checkemail?email=test@example.com")
    assert response.status_code == 200
    assert response.json() == {"message": "사용 가능한 이메일입니다"}

def test_checkemail_unavailable(client, mock_user_crud, mock_current_user):
    mock_user_crud.get_user_by_email.return_value = mock_current_user
    response = client.get("/api/v1/users/checkemail?email=test@example.com")
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 사용중인 이메일입니다"

def test_checkid_available(client, mock_user_crud):
    mock_user_crud.get_user_by_username.return_value = None
    response = client.get("/api/v1/users/checkid?id=testuser")
    assert response.status_code == 200
    assert response.json() == {"message": "사용 가능한 아이디입니다"}

def test_checkid_unavailable(client, mock_user_crud, mock_current_user):
    mock_user_crud.get_user_by_username.return_value = mock_current_user
    response = client.get("/api/v1/users/checkid?id=testuser")
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 사용중인 아이디입니다"

def test_signup(client, mock_user_service, mock_current_user):
    mock_user_service.register_user.return_value = mock_current_user
    payload = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "password123",
        "nickname": "New User"
    }
    response = client.post("/api/v1/users/signup", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com" # Mock returns mock_current_user

def test_login(client, mock_user_service, mock_current_user):
    # Mock return value: (user, access_token, refresh_token)
    mock_user_service.login.return_value = (mock_current_user, "access_token", "refresh_token")
    payload = {
        "account": "testuser", # Fixed: username -> account
        "password": "password123"
    }
    response = client.post("/api/v1/users/login", json=payload)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_read_me(authorized_client, mock_current_user):
    response = authorized_client.get("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == mock_current_user.email

def test_update_user_by_id(authorized_client, mock_user_service, mock_current_user):
    mock_user_service.update_user.return_value = mock_current_user
    payload = {"nickname": "Updated User"}
    response = authorized_client.patch("/api/v1/users/me", json=payload)
    assert response.status_code == 200
    assert response.json()["nickname"] == "Test User" # Mock returns mock_current_user

def test_change_my_pw(authorized_client, mock_user_service):
    mock_user_service.update_pw.return_value = None
    payload = {"old_password": "old", "new_password": "new"}
    response = authorized_client.patch("/api/v1/users/me/password", json=payload)
    assert response.status_code == 200
    assert response.json() == {"msg": "비밀번호 변경 완료"}

def test_delete_me(authorized_client, mock_user_service, mock_current_user):
    mock_user_service.delete_user.return_value = None
    response = authorized_client.delete("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json() == {"deleted": True, "deleted_user_id": mock_current_user.id}

def test_logout(client):
    response = client.post("/api/v1/users/logout")
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_refresh_access(client, mock_user_service):
    mock_user_service.refresh.return_value = "new_access_token"
    client.cookies.set("refresh_token", "valid_refresh_token")
    response = client.post("/api/v1/users/refreshAccess")
    assert response.status_code == 200
    assert response.json() == {"msg": "새 토큰 발급 완료"}

def test_refresh_access_no_token(client):
    response = client.post("/api/v1/users/refreshAccess")
    assert response.status_code == 401
    assert response.json()["detail"] == "refresh token 없음"
