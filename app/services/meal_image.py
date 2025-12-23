from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.meal_image import (
    MealImageResponse,
)
from app.db.models.user import User
from app.db.models.prediction_log import PredictionLog

# from app.db.models.meal_unused import MealImage

# from app.db.crud.meal_image import MealImageCrud
from typing import List
from enum import Enum
from datetime import date
import uuid

from app.services.file_manager import FileManager
from app.clients.ai_client import AIClient


from app.common.image_utils import resize_image

from app.clients.s3_client import S3Client


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

        for image_id in tmp_image_ids:
            try:
                # 1. 로컬 임시 파일 경로 찾기
                tmp_path = FileManager.get_tmp_file_path(image_id)

                # 2. S3 업로드 (Mocking / Skeleton)
                s3_url = S3Client.upload_file(tmp_path, f"meals/{image_id}.jpg")
                image_urls.append(s3_url)

                # 3. Cleanup: S3 업로드 완료 후 로컬 임시 파일 삭제
                await FileManager.delete_tmp_image(tmp_path)

            except FileNotFoundError:
                # 파일이 없는 경우 경고 로그 출력 후 진행
                print(f"Warning: Image file not found for ID {image_id}")
                continue

        return image_urls

    @staticmethod
    async def image_detection(db: AsyncSession, file: UploadFile, current_user_id: int):
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
        await FileManager.save_tmp_image(resized_data, filename)

        try:
            # 4. AI 감지 요청 (AIClient)
            response = await AIClient.request_detection(
                resized_data, image_id, content_type
            )

            # 5. MLOps 구현용 Prediction Log 저장 (실패해도 메인 로직에는 영향 없도록 예외처리)
            try:
                new_log = PredictionLog(
                    image_id=image_id,
                    user_id=current_user_id,
                    raw_response=response,
                    model_version="v4",  # TODO: AI response에 버전 포함되면 교체
                )
                db.add(new_log)
                await db.commit()
            except Exception as e:
                print(f"[PredictionLog Error] Failed to save prediction log: {e}")
                # 로그 저장은 부가 기능이므로 메인 트랜잭션을 방해하지 않게 롤백?
                # or 별도 세션 사용? -> 일단 현재 세션 사용하되 에러시 rollback
                # 하지만 여기서 rollback 하면 메인 로직(있는지 모르겠지만)에도 영향갈 수 있음.
                # 현재는 SELECT나 INSERT가 위쪽에 없으므로 안전.
                await db.rollback()

            return response
        except Exception:
            raise
