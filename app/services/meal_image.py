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
    @staticmethod
    async def image_detection(file: UploadFile, current_user_id: int):
        """
        이미지 업로드 -> 저장 -> AI 감지 요청
        """
        from app.common.image_utils import resize_image
        import uuid

        # 1. 파일 읽기 및 메타데이터 추출
        content = await file.read()
        file_ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
        content_type = file.content_type or "image/jpeg"
        pil_format = "PNG" if file_ext in ["png", "webp"] else "JPEG"

        # 2. 이미지 리사이징 (image_utils)
        resized_data = resize_image(content, format=pil_format)

        # 3. 임시 파일 저장 (FileManager)
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.{file_ext}"
        await FileManager.save_by_bytes(resized_data, filename)

        try:
            # 4. AI 감지 요청 (AIClient)
            return await AIClient.request_detection(
                resized_data, image_id, content_type
            )
        except Exception:
            raise

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
