import pytest
from unittest.mock import patch, AsyncMock
import httpx
from app.clients.ai_client import AIClient
from app.core.settings import settings

# --- AIClient Tests ---
# 외부 API 통신 로직 검증 (Mocking 사용)


@pytest.mark.asyncio
async def test_request_detection_success():
    # Given
    image_data = b"fake-image-bytes"
    image_id = "test-uuid"
    mock_response_data = {"result": "success", "candidates": []}

    # httpx.AsyncClient.post를 메서드 레벨에서 patch (context manager 내부)
    # AIClient 코드: async with httpx.AsyncClient(...) as client: ... await client.post(...)

    # httpx.AsyncClient를 Mocking하여 context manager가 반환하는 client 객체를 제어
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value

        # Prepare Mock Response with Request
        mock_response = httpx.Response(200, json=mock_response_data)
        mock_response._request = httpx.Request("POST", "http://test")

        mock_instance.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # When
        result = await AIClient.request_detection(image_data, image_id)

        # Then
        assert result == mock_response_data

        # Calling verify
        call_args = mock_instance.__aenter__.return_value.post.call_args
        args, kwargs = call_args

        # URL 확인 (v4)
        assert settings.inference_url("v4", "analyze") in args[0] or args[
            0
        ] == settings.inference_url("v4", "analyze")

        # Data 확인
        assert kwargs["data"] == {"image_id": image_id}

        # Files 확인
        filename, content, content_type = kwargs["files"]["image"]
        assert content == image_data


@pytest.mark.asyncio
async def test_request_detection_failure():
    # Given
    image_data = b"fake-image-bytes"
    image_id = "test-uuid"

    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        # 500 에러 응답 설정
        mock_response = httpx.Response(500)
        mock_response._request = httpx.Request("POST", "http://test")

        mock_instance.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # When & Then
        with pytest.raises(httpx.HTTPStatusError):
            await AIClient.request_detection(image_data, image_id)


@pytest.mark.asyncio
async def test_request_single_analysis_success():
    # Given
    food_name = "Kimchi"
    mock_response_data = {"nutritions": {"calories": 100}}

    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value

        mock_response = httpx.Response(200, json=mock_response_data)
        mock_response._request = httpx.Request("POST", "http://test")

        mock_instance.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # When
        result = await AIClient.request_single_analysis(food_name)

        # Then
        assert result == mock_response_data

        # Payload verify
        call_args = mock_instance.__aenter__.return_value.post.call_args
        args, kwargs = call_args

        # Payload 확인
        assert kwargs["json"] == {"food_name": food_name}


@pytest.mark.asyncio
async def test_request_single_analysis_failure():
    # Given
    food_name = "Unknown"

    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        # 404 에러 응답 설정
        mock_response = httpx.Response(404)
        mock_response._request = httpx.Request("POST", "http://test")

        mock_instance.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # When & Then
        with pytest.raises(httpx.HTTPStatusError):
            await AIClient.request_single_analysis(food_name)
