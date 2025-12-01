import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

# --- User Profile Router Tests ---

def test_create_profile_endpoint(authorized_client, mock_user_profile_service, mock_current_user):
    # Response model is UserProfileCreate, which does NOT have age.
    mock_profile = {
        "user_id": mock_current_user.id,
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "birthdate": "1990-01-01"
    }
    mock_user_profile_service.create_profile.return_value = mock_profile

    payload = {
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "birthdate": "1990-01-01"
    }
    
    response = authorized_client.post("/api/v1/users/me/profile/", json=payload)
    
    assert response.status_code == 200
    assert response.json()["gender"] == "male"
    # assert response.json()["age"] == 30 # Removed age check

def test_get_profile_endpoint(authorized_client, mock_user_profile_service, mock_current_user):
    # Response model is UserProfileRead, which has age.
    mock_profile = {
        "id": 1, # alias for profile_id
        "user_id": mock_current_user.id,
        "created_at": datetime.now(timezone.utc),
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "birthdate": "1990-01-01",
        "age": 30
    }
    mock_user_profile_service.get_profile.return_value = mock_profile
    
    response = authorized_client.get("/api/v1/users/me/profile/")
    
    assert response.status_code == 200
    assert response.json()["age"] == 30

def test_update_profile_endpoint(authorized_client, mock_user_profile_service, mock_current_user):
    # Response model is UserProfileRead
    mock_profile = {
        "id": 1,
        "user_id": mock_current_user.id,
        "created_at": datetime.now(timezone.utc),
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "birthdate": "1990-01-01",
        "age": 30
    }
    mock_user_profile_service.update_profile.return_value = mock_profile
    
    payload = {"height": 181.0}
    
    response = authorized_client.patch("/api/v1/users/me/profile/", json=payload)
    
    assert response.status_code == 200
    assert response.json()["age"] == 30

# --- Profile Form Tests ---

def test_create_profile_form_endpoint(authorized_client, mock_profile_form_service, mock_current_user):
    # Response model is ProfileFormResponse
    mock_response = {
        "user_id": mock_current_user.id,
        "created_at": datetime.now(timezone.utc),
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "conditions": ["None"]
    }
    mock_profile_form_service.create_profile_form.return_value = mock_response
    
    payload = {
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "conditions": ["None"]
    }
    
    response = authorized_client.post("/api/v1/users/me/profile/form", json=payload)
    
    assert response.status_code == 200
    assert response.json()["conditions"] == ["None"]

def test_get_profile_form_endpoint(authorized_client, mock_profile_form_service, mock_current_user):
    # Response model is ProfileFormRead
    mock_response = {
        "user_id": mock_current_user.id,
        "created_at": datetime.now(timezone.utc),
        "gender": "male",
        "height": 180.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "conditions": ["None"],
        "age": 30
    }
    mock_profile_form_service.read_profile_form.return_value = mock_response
    
    response = authorized_client.get("/api/v1/users/me/profile/form")
    
    assert response.status_code == 200
    assert response.json()["age"] == 30

def test_update_profile_form_endpoint(authorized_client, mock_profile_form_service, mock_current_user):
    # Response model is ProfileFormUpdate, which does NOT have age.
    mock_response = {
        "height": 181.0,
        "weight": 75.0,
        "goal_type": "maintain",
        "conditions": ["None"]
    }
    # The service might return the updated data dict or object
    # The router returns profile_data (the input payload + updates)
    # Actually router code: await ...; return profile_data
    # So response will be the payload sent + defaults?
    # ProfileFormUpdate schema has optional fields.
    
    payload = {"height": 181.0}
    
    response = authorized_client.patch("/api/v1/users/me/profile/form", json=payload)
    
    assert response.status_code == 200
    assert response.json()["height"] == 181.0
