import os
import shutil
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Optional


class FileManager:
    """
    로컬 파일 시스템 관리 (Local I/O)
    - 책임: 임시 파일(tmp) 생성, 조회, 삭제 전담
    - 특징: 비즈니스 로직(ID생성, 리사이징) 몰라야 함, Static Interface 유지
    """

    TEMP_DIR = (
        "/tmp/caloreat_images"  # TODO: 환경변수로 변경 필요 (도커파일추가시 경로유연성)
    )

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls.TEMP_DIR, exist_ok=True)

    @staticmethod
    async def delete_tmp_image(file_path: str) -> None:
        """
        로컬 파일 시스템에서 파일을 삭제 (Non-blocking)
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            # 삭제 실패 시 로그 남기기
            print(f"Error deleting file {file_path}: {e}")
            pass

    @staticmethod
    async def save_tmp_image(image_data: bytes, filename: str) -> str:
        """
        바이트 데이터를 임시 경로에 저장 (Non-blocking)
        """
        FileManager._ensure_dir()
        file_path = os.path.join(FileManager.TEMP_DIR, filename)

        # 현재는 단순 동기 쓰기 (TODO:트래픽 증가 시 Threadpool 적용)
        with open(file_path, "wb") as f:
            f.write(image_data)
        return file_path

    @staticmethod
    def get_tmp_file_path(image_id: str) -> str:
        """
        이미지 ID(UUID)를 기반으로 실제 파일 경로 검색
        """
        FileManager._ensure_dir()
        try:
            for filename in os.listdir(FileManager.TEMP_DIR):
                if filename.startswith(image_id) and filename[len(image_id)] == ".":
                    return os.path.join(FileManager.TEMP_DIR, filename)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Image directory not found: {FileManager.TEMP_DIR}"
            )

        raise FileNotFoundError(f"Image file not found for ID: {image_id}")


# --- Legacy Validation Logic (from feat/meal-s3) ---
# MVP 기능 구동 우선 모든 validation 비활성화
# 추후 필요시 활성화하여 사용

# ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
# MAX_FILE_SIZE_MB = 10

# def _validate_extension(filename: str):
#     ext = filename.rsplit(".", 1)[-1].lower()
#     if ext not in ALLOWED_EXTENSIONS:
#         raise HTTPException(status_code=400, detail=f"Unsupported file extension: .{ext}")

# def _validate_mime(file: UploadFile):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail=f"Invalid MIME type: {file.content_type}")

# def _validate_size(file: UploadFile):
#     file.file.seek(0, os.SEEK_END)
#     size = file.file.tell()
#     file.file.seek(0)
#     max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
#     if size > max_bytes:
#         raise HTTPException(status_code=400, detail=f"File size exceeds limit of {MAX_FILE_SIZE_MB} MB")
