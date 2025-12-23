import pytest
import io
from PIL import Image
from unittest.mock import AsyncMock, patch
from app.db.models.prediction_log import PredictionLog


def create_dummy_image_bytes():
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), "white")
    image.save(file, "jpeg")
    file.name = "test.jpg"
    file.seek(0)
    return file.read()


def test_prediction_log_saved_on_upload(
    authorized_client,
    mock_db_session,
):
    """
    [MLOps] 이미지 업로드 시 PredictionLog가 저장되는지 테스트 (Mock DB & Mock AI)
    """
    # 0. Setup
    image_content = create_dummy_image_bytes()
    files = {"file": ("test.jpg", image_content, "image/jpeg")}

    # Mock AI Response
    mock_response = {
        "image_id": "test-uuid",
        "food_name": "Kimchi",
        "candidates": [{"label": "Kimchi", "confidence": 0.99}],
    }

    # 1. Action: Upload Image
    # We maintain the patch for AIClient and FileManager (to avoid saving locally)
    with (
        patch(
            "app.clients.ai_client.AIClient.request_detection", new_callable=AsyncMock
        ) as mock_ai,
        patch(
            "app.services.file_manager.FileManager.save_tmp_image",
            new_callable=AsyncMock,
        ) as mock_save,
        patch(
            "app.services.file_manager.FileManager.get_tmp_file_path",
            return_value="/tmp/test.jpg",
        ),
    ):

        mock_ai.return_value = mock_response

        response = authorized_client.post("/api/v1/meals/upload", files=files)

    # 2. Assert API Response
    assert response.status_code == 200
    data = response.json()
    assert data["food_name"] == "Kimchi"

    # 3. Assert DB Side Effect (PredictionLog)
    # mock_db_session.add가 호출되었는지 확인
    # 인자로 넘어온 객체가 PredictionLog 인스턴스인지, 내용이 맞는지 확인
    mock_db_session.add.assert_called_once()

    # 호출된 인자 가져오기
    args, _ = mock_db_session.add.call_args
    saved_log = args[0]

    # 내용 검증
    assert isinstance(saved_log, PredictionLog)
    assert saved_log.raw_response == mock_response
    # current_user.id is 1 from conftest.py
    assert saved_log.user_id == 1

    # commit 호출 확인
    mock_db_session.commit.assert_called_once()
