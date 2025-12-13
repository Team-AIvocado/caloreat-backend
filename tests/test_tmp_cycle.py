import pytest
import os
import uuid
from unittest.mock import patch, MagicMock
from app.services.file_manager import FileManager
from app.services.meal_image import MealImageService

# --- TMP Image Lifecycle Tests ---
# 파일 시스템 조작 및 정리(Cleanup) 로직 검증


@pytest.fixture
def mock_temp_dir(tmp_path):
    """
    FileManager.TEMP_DIR을 pytest의 tmp_path(임시 디렉토리)로 교체
    테스트 종료 후 자동 삭제됨
    """
    tmp_dir = str(tmp_path / "caloreat_images")
    with patch("app.services.file_manager.FileManager.TEMP_DIR", tmp_dir):
        yield tmp_dir


@pytest.mark.asyncio
async def test_file_manager_save_and_get(mock_temp_dir):
    # Given
    image_data = b"test-image-content"
    image_id = str(uuid.uuid4())
    filename = f"{image_id}.jpg"

    # When: 저장
    saved_path = await FileManager.save_tmp_image(image_data, filename)

    # Then: 파일 존재 확인
    assert os.path.exists(saved_path)
    assert os.path.isfile(saved_path)
    with open(saved_path, "rb") as f:
        assert f.read() == image_data

    # When: 조회
    found_path = FileManager.get_tmp_file_path(image_id)

    # Then: 경로 일치 확인
    assert found_path == saved_path


@pytest.mark.asyncio
async def test_file_manager_delete(mock_temp_dir):
    # Given
    image_data = b"to-be-deleted"
    filename = "delete_me.jpg"
    saved_path = await FileManager.save_tmp_image(image_data, filename)
    assert os.path.exists(saved_path)

    # When: 삭제
    await FileManager.delete_tmp_image(saved_path)

    # Then: 파일 제거 확인
    assert not os.path.exists(saved_path)


@pytest.mark.asyncio
async def test_upload_service_lifecycle(mock_temp_dir):
    """
    MealImageService.upload_tmp_images_to_s3 호출 시:
    1. 로컬 파일 읽기
    2. S3 업로드 (Mock)
    3. 로컬 파일 삭제 (검증 대상)
    """
    # Given
    image_id = str(uuid.uuid4())
    filename = f"{image_id}.jpg"
    image_data = b"lifecycle-test-data"

    # 1. 로컬 파일 미리 생성
    saved_path = await FileManager.save_tmp_image(image_data, filename)
    assert os.path.exists(saved_path)

    # Mocking S3 Client
    with patch("app.clients.s3_client.S3Client.upload_file") as mock_upload:
        mock_upload.return_value = "https://s3.bucket.com/image.jpg"

        # When: 서비스 호출
        uploaded_urls = await MealImageService.upload_tmp_images_to_s3([image_id])

        # Then
        # 1. S3 업로드 호출 확인
        mock_upload.assert_called_once()
        args, _ = mock_upload.call_args
        assert args[0] == saved_path  # 첫번째 인자가 파일 경로

        # 2. 결과 URL 반환 확인
        assert len(uploaded_urls) == 1
        assert uploaded_urls[0] == "https://s3.bucket.com/image.jpg"

        # 3. ★ 핵심: 로컬 파일 삭제 확인 ★
        assert not os.path.exists(
            saved_path
        ), "S3 업로드 후 로컬 파일이 삭제되지 않았습니다."
