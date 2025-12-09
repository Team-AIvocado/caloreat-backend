import os
import uuid
import shutil
from fastapi import UploadFile
from typing import Optional


class FileManager:
    """
    임시 파일의 저장 및 정리를 관리
    """

    @staticmethod
    async def save_tmp_image(file: UploadFile) -> str:
        """
        업로드된 파일을 UUID 파일명을 사용하여 임시 경로에 저장

        Returns:
            str: 저장된 임시 파일의 절대 경로
        """
        # 임시 디렉토리 설정 (없으면 생성)
        tmp_dir = "/tmp/caloreat_images"
        os.makedirs(tmp_dir, exist_ok=True)

        # 원본 파일명에서 확장자 추출
        file_ext = file.filename.split(".")[-1] if file.filename else "jpg"

        # 상태유지 이미지 식별자 (UUID)
        image_id = str(uuid.uuid4())

        # 저장될 파일명 (unique)
        filename = f"{image_id}.{file_ext}"
        file_path = os.path.join(tmp_dir, filename)

        # 파일 저장
        try:
            with open(file_path, "wb") as buffer:
                # shutil 로직: 대용량 파일도 버퍼링을 통해 복사
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            # 파일 저장 실패 시 에러 처리 (로그 등)
            raise e
        finally:
            await file.seek(0)  # 파일 포인터 초기화 (필요 시)

        return file_path

    @staticmethod
    async def delete_tmp_image(file_path: str) -> None:
        """
        로컬 파일 시스템에서 파일을 삭제

        Args:
            file_path (str): 삭제할 파일의 절대 경로
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            # 삭제 실패 시 로그 남기기 (여기서는 print로 대체하거나 logging 모듈 사용)
            print(f"Error deleting file {file_path}: {e}")
            # 필요에 따라 예외를 다시 발생시키지 않고 넘어갈 수 있음
            pass
