from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User

# from app.db.models.meal_unused import MealImage

# from app.db.crud.meal_image import MealImageCrud
from app.services.file_manager import FileManager
from app.clients.ai_client import AIClient
from typing import List
from enum import Enum
from datetime import date
import os


class MealItemService:
    # FileManager로 임시저장 -> AIClient.request_detection 호출 -> 반환 -> FileManager로 임시파일 삭제
    @staticmethod
    async def image_detection(file: UploadFile, current_user_id: int):
        """
        이미지 업로드 -> 저장 -> AI 감지 요청
        """
        # 1. 파일 임시 저장
        # FileManager.save_tmp_image는 저장된 절대 경로를 반환합니다.
        file_path = await FileManager.save_tmp_image(file)

        try:
            # 2. 이미지 파일 읽기
            # 저장된 파일을 바이너리 모드("rb")로 열어서 내용을 읽습니다.
            with open(file_path, "rb") as f:
                image_data = f.read()

            # 3. AI 서버 요청 (Detection)
            # 파일 경로에서 파일명 추출 (UUID로 되어 있음) -> image_id로 사용
            image_id = os.path.basename(file_path).split(".")[0]

            # AIClient에게 감지 요청
            detection_result = await AIClient.request_detection(image_data, image_id)

            # 5. 결과 반환
            # 받은 결과를 그대로 반환하거나, 필요 시 Pydantic 모델로 변환(MealImageResponse 등)할 수 있습니다.
            return detection_result

        finally:
            # 4. 임시 파일 삭제
            # 로직 수행 후(성공/실패 여부와 상관없이) 임시 파일은 반드시 삭제합니다.
            await FileManager.delete_tmp_image(file_path)

    # AIClient.request_analysis 호출하여 음식 리스트에 대한 영양소 분석 및 반환
    @staticmethod
    async def food_analysis(food_list: List[dict]):
        """
        음식 리스트 -> AI 영양소 분석 요청
        """
        # 1. 입력 데이터 가공 (필요시)
        # food_list 형식이 AIClient가 원하는 형식([{"image_id":..., "foodname":...}])과 일치한다고 가정합니다.

        # 2. AI 서버 요청 (Analysis)
        analysis_result = await AIClient.request_analysis(food_list)

        # 3. 결과 반환
        return analysis_result
