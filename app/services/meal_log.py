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


from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem
from app.db.schemas.meal_log import MealLogCreate

from app.services.file_manager import FileManager
import os


class MealLogService:
    @staticmethod
    async def create_meal_log(
        db: AsyncSession, current_user_id: int, meal_create: MealLogCreate
    ):
        try:
            # 1. 이미지 처리 (tmp -> S3)
            # - tmp 경로 찾기
            # - S3 업로드 (현재는 Mocking)
            # - 로컬 파일 정리
            # meal log에 저장할 image_url
            image_urls = []
            if meal_create.tmp_image_ids:

                # S3 Client Skeleton (활성화 시 주석 해제)
                # from app.clients.s3_client import S3Client

                for image_id in meal_create.tmp_image_ids:
                    try:
                        # 로컬 임시 파일 경로 찾기
                        tmp_path = FileManager.get_tmp_file_path(image_id)

                        # TODO: [S3 Upload Skeleton] - 실제 구현 시 주석 해제 및 사용
                        # s3_url = S3Client.upload_file(tmp_path, f"meals/{image_id}.jpg")

                        # [Mocking] 더미 URL 생성 (검증용)
                        s3_url = f"https://s3.ap-northeast-2.amazonaws.com/caloreat-bucket/meals/{image_id}.jpg"
                        image_urls.append(s3_url)

                        # [Cleanup] S3 승격 완료 후 로컬 임시 파일 삭제
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

                    except FileNotFoundError:
                        # 파일이 없는 경우 경고 로그 출력 후 진행
                        print(f"Warning: Image file not found for ID {image_id}")
                        continue

            # TODO: 다음 단계에서 DB 저장 로직 구현
            return {"status": "processing_images", "image_urls": image_urls}

        except Exception as e:
            raise e
