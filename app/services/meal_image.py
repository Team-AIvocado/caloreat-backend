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

from app.services.file_manager import FileManager
from app.clients.ai_client import AIClient

import os

from app.common.image_utils import resize_image


# Meal Service
class MealImageService:
    @staticmethod
    async def upload_tmp_images_to_s3(tmp_image_ids: list[str]) -> list[str]:
        """
        임시 이미지 ID 목록을 받아 S3로 업로드하고 URL 리스트를 반환
        local tmp 파일은 업로드 후 삭제
        """
        image_urls = []
        if not tmp_image_ids:
            return image_urls

        # S3 Client Skeleton (활성화 시 주석 해제)
        # from app.clients.s3_client import S3Client

        for image_id in tmp_image_ids:
            try:
                # 1. 로컬 임시 파일 경로 찾기
                tmp_path = FileManager.get_tmp_file_path(image_id)

                # 2. S3 업로드 (Mocking / Skeleton)
                # 실제 구현 시: s3_url = S3Client.upload_file(tmp_path, f"meals/{image_id}.jpg")

                # [Mocking] 더미 URL 생성
                s3_url = f"https://s3.ap-northeast-2.amazonaws.com/caloreat-bucket/meals/{image_id}.jpg"
                image_urls.append(s3_url)

                # 3. [Cleanup] S3 승격 완료 후 로컬 임시 파일 삭제
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            except FileNotFoundError:
                # 파일이 없는 경우 경고 로그 출력 후 진행
                print(f"Warning: Image file not found for ID {image_id}")
                continue

        return image_urls

    @staticmethod
    async def image_detection(file: UploadFile, current_user_id: int):
        """
        이미지 업로드 -> 저장 -> AI 감지 요청
        """

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
