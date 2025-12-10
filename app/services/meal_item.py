from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User

# from app.db.models.meal_unused import MealImage

# from app.db.crud.meal_image import MealImageCrud
from datetime import date
import os


class MealItemService:
    # AIClient.request_analysis 호출하여 음식 리스트에 대한 영양소 분석 및 반환
    @staticmethod
    async def food_analysis(food_list: list[dict]):
        """
        음식 리스트 -> AI 영양소 분석 요청
        """
        # 1. 입력 데이터 가공 (필요시)
        # food_list 형식이 AIClient가 원하는 형식([{"image_id":..., "foodname":...}])과 일치한다고 가정

        # 2. AI 서버 요청 (Analysis)
        analysis_result = await AIClient.request_analysis(food_list)

        # 3. 결과 반환
        return analysis_result

    # 임시.. 이동예정
