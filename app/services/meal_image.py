from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User

# from app.db.models.meal_unused import MealImage

# from app.db.crud.meal_image import MealImageCrud
from typing import List
from enum import Enum
from datetime import date
import uuid
import os  # FileManager에서 저장한 파일 경로 파싱용
from app.services.file_manager import FileManager
from app.clients.ai_client import AIClient


# Meal Service
class MealImageService:
    # --- 이미지 -> 음식이름반환 ---
    # FileManager로 임시저장 -> AIClient.request_detection 호출 -> 반환 -> FileManager로 임시파일 삭제
    @staticmethod
    async def image_detection(file: UploadFile, current_user_id: int):
        """
        이미지 업로드 -> 저장 -> AI 감지 요청
        """
        # 1. 파일 임시 저장
        # FileManager.save_tmp_image는 저장된 절대 경로를 반환
        file_path = await FileManager.save_tmp_image(file)

        try:
            # 2. 이미지 파일 읽기
            # 저장된 파일을 바이너리 모드("rb")로 read
            with open(file_path, "rb") as f:
                image_data = f.read()

            # 3. AI 서버 요청 (Detection)
            # 저장된 파일명에서 UUID 추출 (파일명 형식이 {uuid}.{ext})
            # FileManager.save_tmp_image 내부에서 UUID를 생성하여 파일명으로 사용함
            filename = os.path.basename(file_path)
            image_id = os.path.splitext(filename)[0]

            # AIClient에게 감지 요청 (일관된 image_id 사용)
            detection_result = await AIClient.request_detection(image_data, image_id)

            # 5. 결과 반환
            # 받은 결과를 그대로 반환하거나, 필요 시 Pydantic 모델로 변환(MealImageResponse 등)
            return detection_result

        except Exception:
            raise
        # finally:  -> 마지막 단계로 들어가야함
        #     # 4. 임시 파일 삭제
        #     # 로직 수행 후(성공/실패 여부와 상관없이) 임시 파일은 반드시 삭제
        #     await FileManager.delete_tmp_image(file_path)

    # @staticmethod
    # async def create(db: AsyncSession, user_id: int, file: UploadFile):
    #     pass
    #     # orm = await MealImageCrud.create(db, user_id, file)
    #     # await db.commit()
    #     # await db.refresh(orm)
    #     # return orm

    # @staticmethod
    # async def get(db, user_id):
    #     pass
    #     # orm = await MealImageCrud.get(db, user_id)
    #     # return orm

    # @staticmethod
    # async def update(db, user_id, payload):
    #     pass
    #     # orm = await MealImageCrud.update(db, user_id, payload)
    #     # await db.commit()
    #     # await db.refresh(orm)
    #     # return orm

    # @staticmethod
    # async def delete(db, user_id):
    #     pass
    #     # await MealImageCrud.delete(db, user_id)
    #     # await db.commit()
