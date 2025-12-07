import json
import httpx
from typing import Any, Dict, List, Optional
from app.core.settings import settings

# 외부 AI/LLM 서버와 통신하여 음식 이미지 식별 및 영양소 분석을 요청하는 클라이언트 역할


class AIClient:
    """
    외부 AI/LLM 서버와 상호작용하기 위한 클라이언트
    음식 객체 감지 및 영양분 분석 요청을 처리
    """

    @staticmethod
    async def request_detection(image_data: bytes, image_id: str) -> Dict[str, Any]:
        """
        AI 서버에 이미지를 전송하여 음식 감지 요청

        """
        async with httpx.AsyncClient() as client:
            files = {"image": ("image.jpg", image_data, "image/jpeg")}
            data = {"image_id": image_id}

            # 실제 연결 시 타임아웃 설정 고려 필요
            response = await client.post(
                settings.ai_detection_url, data=data, files=files
            )
            # 응답 코드가 200번대가 아닐 경우 예외처리
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def request_analysis(foods: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        LLM 서버에 감지된 음식들의 영양소 분석을 요청

        """
        async with httpx.AsyncClient() as client:
            payload = {"foods": foods}

            response = await client.post(
                settings.ai_analysis_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
