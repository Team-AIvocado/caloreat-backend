import json
import httpx
from typing import Any, Dict, Optional
from app.core.settings import settings

# 외부 AI/LLM 서버와 통신하여 음식 이미지 식별 및 영양소 분석을 요청하는 클라이언트 역할

#
inference_url_v1 = settings.inference_url("v1", "analyze")
inference_url_v2 = settings.inference_url("v2", "analyze")
inference_url_v3 = settings.inference_url("v3", "analyze")
inference_url_v4 = settings.inference_url("v4", "analyze")
# llm_url_v1 = settings.llm_url("v1", "nutrition")


class AIClient:
    """
    외부 AI/LLM 서버와 상호작용하기 위한 클라이언트
    음식 객체 감지 및 영양분 분석 요청을 처리
    """

    @staticmethod
    # v4만 실행(임시)
    # TODO: confidence 분기 추가 필요
    async def request_detection(
        image_data: bytes, image_id: str, content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        AI 서버에 이미지를 전송하여 음식 감지 요청

        """
        try:
            # 30초 타임아웃시 롤백
            async with httpx.AsyncClient(timeout=30.0) as client:
                filename = "image.png" if content_type == "image/png" else "image.jpg"
                files = {"image": (filename, image_data, content_type)}
                data = {"image_id": image_id}

                # 실제 연결 시 타임아웃 설정 고려 필요
                response = await client.post(inference_url_v4, data=data, files=files)
                # 응답 코드가 200번대가 아닐 경우 예외처리
                response.raise_for_status()
                return response.json()
        except Exception:
            raise

    # nutrition analysis
    # /nutrition
    @staticmethod
    async def request_single_analysis(foodname: str) -> dict[str, Any]:
        """
        LLM 서버에 단일 음식 영양소 분석을 요청
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {"food_name": foodname}

                response = await client.post(
                    settings.llm_url("nutrition"),
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            raise

    # 다중음식 영양소 분석
    # @staticmethod
    # async def request_analysis(foods: list[dict[str, str]]) -> dict[str, Any]:
    #     """
    #     LLM 서버에 감지된 음식들의 영양소 분석을 요청 (기존 리스트 방식)
    #     """
    #     try:
    #         async with httpx.AsyncClient(timeout=30.0) as client:
    #             payload = {"foods": foods}

    #             response = await client.post(
    #                 f"{settings.ai_analysis_url}/nutrition",
    #                 json=payload,
    #             )
    #             response.raise_for_status()
    #             return response.json()
    #     except Exception:
    #         raise
