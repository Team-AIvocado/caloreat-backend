import pytest
from unittest.mock import AsyncMock

# --- Health Condition Router Tests ---

def test_create_condition_endpoint(authorized_client, mock_health_condition_service, mock_current_user):
    # Mock return value
    mock_condition = {
        "id": 1,
        "conditions": "Diabetes"
    }
    mock_health_condition_service.create_one_condition.return_value = mock_condition

    payload = {
        "conditions": "Diabetes"
    }
    
    response = authorized_client.post("/api/v1/users/me/heatlh-conditions/", json=payload)
    
    assert response.status_code == 200
    assert response.json() == mock_condition
