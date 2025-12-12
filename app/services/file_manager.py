import os
import uuid
import mimetypes
import shutil
from fastapi import UploadFile
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Optional

# FileManager tmp lifecycle CRUD


class FileManager:
    """
    실서비스용 FileManager.
    -> 임시 디렉토리에 파일 저장
    -> 확장자/크기/MIME 검증
    -> UUID 기반 파일명 생성
    """

    TEMP_DIR = "/tmp"
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    MAX_FILE_SIZE_MB = 10 # 업로드 파일 최대 10MB(서버 메모리와 I/O 부담을 막기 위해)

    def __init__(self):
        os.makedirs(self.TEMP_DIR, exist_ok=True)

    def _validate_extension(self, filename: str):
        """
        허용되지 않은 확장자 방지.
        """
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension: .{ext}",
            )
        
    def _validate_mime(self, file: UploadFile):
        """
        MIME 타입 검사 (이미지인지 확인)
        """
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid MIME type: {file.content_type}",
            )
        
    def _validate_size(self, file: UploadFile):
    임시 파일의 저장 및 정리를 관리
    """

    @staticmethod
    async def delete_tmp_image(file_path: str) -> None:
        """
        업로드 파일의 크기가 제한을 초과하는지 확인.
        (UploadFile은 크기 정보를 바로 주지 않으므로 read 후 체크)
        로컬 파일 시스템에서 파일을 삭제
        Args:
            file_path (str): 삭제할 파일의 절대 경로
        """
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        max_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds limit of {self.MAX_FILE_SIZE_MB} MB",
            )
        
    def save_temp_file(self, file: UploadFile) -> str:

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            # 삭제 실패 시 로그 남기기 (여기서는 print로 대체하거나 logging 모듈 사용)
            print(f"Error deleting file {file_path}: {e}")
            pass

        # def _delete():
        #     try:
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #     except OSError as e:
        #         # 삭제 실패 시 로그 남기기 (여기서는 print로 대체하거나 logging 모듈 사용)
        #         print(f"Error deleting file {file_path}: {e}")
        #         pass

        # await run_in_threadpool(_delete)

    @staticmethod
    async def save_tmp_image(image_data: bytes, filename: str) -> str:
        """
        UploadFile을 TEMP_DIR에 안전하게 저장하고 경로 반환.
        """
        # 검증 단계
        self._validate_extension(file.filename)
        self._validate_mime(file)
        self._validate_size(file)

        # 고유한 파일명 생성 (사용자 파일명 사용 금지)
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"

        # 최종 저장 경로
        file_path = os.path.join(self.TEMP_DIR, filename)
        바이트 데이터를 임시 경로에 저장 (Non-blocking)
        """
        tmp_dir = "/tmp/caloreat_images"
        os.makedirs(tmp_dir, exist_ok=True)

        file_path = os.path.join(tmp_dir, filename)

        # 파일 저장
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to save file to server",
            )

        # TODO:
        # def _write():
        #     with open(file_path, "wb") as f:
        #         f.write(image_data)
        #     return file_path

        # return await run_in_threadpool(_write)

        with open(file_path, "wb") as f:
            f.write(image_data)
        return file_path

    def remove_temp_file(self, file_path: str):
        """
        S3 업로드가 끝난 후 임시 파일 삭제.
        """
        if os.path.exists(file_path):
            os.remove(file_path)



    # 식단 저장, S3 업로드 flow
    @staticmethod
    def get_tmp_file_path(image_id: str) -> str:
        """
        이미지 ID로부터 임시 파일 경로를 반환

        Args:
            image_id (str): 업로드된 이미지의 UUID

        Returns:
            str: 임시 파일의 절대 경로
        """
        tmp_dir = "/tmp/caloreat_images"

        # 저장 시 원본 확장자를 유지하므로 (예: {uuid}.png),
        # UUID만으로는 확장자를 알 수 없어 디렉토리 검색이 필요함.

        # 해당 ID로 시작하는 파일 찾기 스캔
        try:
            for filename in os.listdir(tmp_dir):
                # UUID가 정확히 매칭되는지 확인 (파일명: {uuid}.{ext})
                if filename.startswith(image_id) and filename[len(image_id)] == ".":
                    return os.path.join(tmp_dir, filename)
        except FileNotFoundError:
            # tmp 디렉토리가 없는 경우 등
            raise FileNotFoundError(f"Image directory not found: {tmp_dir}")

        # 파일을 찾지 못한 경우 명시적 에러 발생
        raise FileNotFoundError(f"Image file not found for ID: {image_id}")
