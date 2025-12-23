import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from datetime import date

# --- Meal Router Tests ---
# 각 엔드포인트가 정상적으로 라우팅되고, 권한 검사를 수행하며,
# 서비스 계층을 올바르게 호출하는지 검증합니다. (Service Logic Mocking)


def test_upload_image_unauthorized(client):
    response = client.post("/api/v1/meals/upload")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_image_authorized(authorized_client):
    # Mocking Service
    mock_detection_result = {
        "image_id": "test-uuid",
        "food_name": "된장찌개",
        "candidates": [{"label": "된장찌개", "confidence": 0.9}],
    }

    with patch(
        "app.services.meal_image.MealImageService.image_detection",
        new_callable=AsyncMock,
    ) as mock_service:
        mock_service.return_value = mock_detection_result

        # 파일 업로드 시뮬레이션 (dummy)
        response = authorized_client.post(
            "/api/v1/meals/upload",
            files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["image_id"] == "test-uuid"
        mock_service.assert_called_once()


def test_override_prediction_unauthorized(client):
    response = client.post("/api/v1/meals/override/image")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_override_prediction_authorized(authorized_client):
    # Mocked Endpoint in Router (No Service call)
    response = authorized_client.post(
        "/api/v1/meals/override/image",
        files={"file": ("retry.jpg", b"data", "image/jpeg")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("corrected") is True


def test_food_search_manual(client):
    # Correct Path: /foods/manual from router
    response = client.get("/api/v1/meals/foods/manual?query=된장")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert isinstance(results, list)
    # Mock data check (from router implementation)
    # all_foods = ["된장찌개", "된장국", ...]
    assert "된장찌개" in results


def test_analyze_single_image(client):
    # Correct Path: /analyze/single
    request_payload = {"foodname": "된장찌개"}

    mock_analysis_result = {
        "foodname": "된장찌개",
        "nutritions": {"calories": 200, "carbs": 20, "protein": 10, "fat": 5},
    }

    with patch(
        "app.services.meal_item.MealItemService.one_food_analysis",
        new_callable=AsyncMock,
    ) as mock_service:
        mock_service.return_value = mock_analysis_result

        response = client.post("/api/v1/meals/analyze/single", json=request_payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["foodname"] == "된장찌개"
        mock_service.assert_called_once()


def test_create_meal_log_unauthorized(client):
    response = client.post("/api/v1/meals/log", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_meal_log_authorized(authorized_client):
    payload = {
        "meal_type": "snack",
        "eaten_at": "2025-12-06T12:00:00",
        "tmp_image_ids": ["uuid-1"],
        "meal_items": [
            {
                "foodname": "test_food",
                "quantity": 100,
                "nutritions": {"calories": 100, "carbs": 10, "protein": 5, "fat": 2},
            }
        ],
    }

    # IMPORTANT: Mocking the Service to return a Pydantic Model (MealLogRead) or dict.
    # Since we changed Service to return MealLogRead, the mock should ideally reflect that.
    # However, returning a dict is also fine because FastAPI handles Pydantic serialization.
    # The key test here is whether the ROUTER filters out 'user_id' if it somehow leaks.
    # So we will inject 'user_id' into the mock return value to VERIFY that the router strips it.

    mock_log_response = {
        "id": 100,
        "user_id": 1,  # <--- INJECTED LEAK: This simulates the Service passing sensitive data
        "meal_type": "snack",
        "eaten_at": "2025-12-06T12:00:00",
        "created_at": "2025-12-06T12:00:00",
        "updated_at": "2025-12-06T12:00:00",
        "image_urls": ["http://s3/img.jpg"],
        "meal_items": [],
    }

    with patch(
        "app.services.meal_log.MealLogService.create_meal_log",
        new_callable=AsyncMock,
    ) as mock_service:
        mock_service.return_value = mock_log_response

        response = authorized_client.post("/api/v1/meals/log", json=payload)

        # 422 Validation Error check
        if response.status_code == 422:
            print(response.json())

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["meal_type"] == "snack"

        # ★ SECURITY CHECK: Verify that user_id is STRIPPED from response
        assert "user_id" not in response.json()

        mock_service.assert_called_once()


def test_read_meal_logs_unauthorized(client):
    response = client.get("/api/v1/meals/logs")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_meal_logs_authorized(authorized_client):
    # Mock Data: DB에는 원본 URL 저장
    mock_db_log = {
        "id": 1,
        "user_id": 1,
        "meal_type": "breakfast",
        "eaten_at": "2025-12-06T08:00:00",
        "image_urls": ["https://s3.original.com/meals/uuid.jpg"],
        "meal_items": [],
        "created_at": "2025-12-06T08:00:00",
    }

    # Mocking CRUD and S3Client to verify Service Logic
    # Service 자체는 Mock하지 않고 실제 로직(URL 변환)을 태움
    with (
        patch(
            "app.db.crud.meal_log.MealLogCrud.get_meal_logs_db", new_callable=AsyncMock
        ) as mock_crud,
        patch(
            "app.clients.s3_client.S3Client.generate_presigned_url"
        ) as mock_s3_generate,
    ):

        # CRUD는 DB 객체(dict 호환) 반환
        # Pydantic schema validation을 통과하기 위해 dict 형태 혹은 object 형태 필요
        # 여기서는 MagicMock으로 속성 접근 가능하게 설정 혹은 dict 반환
        # Service 코드에서 `if log.image_urls:` 접근하므로 객체처럼 동작해야 함

        # Simple Mock Object mimicking ORM model
        from unittest.mock import MagicMock

        mock_orm_obj = MagicMock()
        mock_orm_obj.id = 1
        mock_orm_obj.user_id = 1
        mock_orm_obj.meal_type = "breakfast"
        mock_orm_obj.eaten_at = date(2025, 12, 6)
        mock_orm_obj.image_urls = ["https://s3.original.com/meals/uuid.jpg"]
        mock_orm_obj.meal_items = []
        mock_orm_obj.created_at = "2025-12-06T08:00:00"

        mock_crud.return_value = [mock_orm_obj]

        # S3 Client는 서명된 URL 반환
        mock_s3_generate.return_value = (
            "https://s3.signed.com/meals/uuid.jpg?signature=xyz"
        )

        # Request
        response = authorized_client.get("/api/v1/meals/logs?date=2025-12-06")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        # [Verification] 반환된 URL이 Presigned URL이어야 함
        assert (
            data[0]["image_urls"][0]
            == "https://s3.signed.com/meals/uuid.jpg?signature=xyz"
        )

        # [Verification] DB는 건드리지 않고, S3 generate가 호출되었는지 확인
        mock_s3_generate.assert_called_once()


def test_update_meal_log_unauthorized(client):
    response = client.put("/api/v1/meals/log/123", json={})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_meal_log_authorized(authorized_client):
    payload = {
        "meal_type": "dinner",
        "eaten_at": "2025-12-06T18:00:00",
        "meal_items": [],  # Empty list for simple update mock
    }

    with patch(
        "app.services.meal_log.MealLogService.update_meal_log",
        new_callable=AsyncMock,
    ) as mock_service:
        # Return whatever Structure is expected, basic dict works for Pydantic response usually
        mock_service.return_value = {
            "id": 123,
            "user_id": 1,
            "meal_type": "dinner",
            "eaten_at": "2025-12-06T18:00:00",
            "created_at": "2025-12-06T12:00:00",
            "updated_at": "2025-12-06T12:00:00",
            "image_urls": [],
            "meal_items": [],
        }

        response = authorized_client.put("/api/v1/meals/log/123", json=payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["meal_type"] == "dinner"


def test_delete_meal_log_unauthorized(client):
    response = client.delete("/api/v1/meals/log/123")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_meal_log_authorized(authorized_client):
    with patch(
        "app.services.meal_log.MealLogService.delete_meal_log",
        new_callable=AsyncMock,
    ) as mock_service:
        mock_service.return_value = True

        response = authorized_client.delete("/api/v1/meals/log/123")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() is True
