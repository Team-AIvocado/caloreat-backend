import os
import uuid
import mimetypes
from fastapi import UploadFile
from fastapi import HTTPException

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
        """
        업로드 파일의 크기가 제한을 초과하는지 확인.
        (UploadFile은 크기 정보를 바로 주지 않으므로 read 후 체크)
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

        # 파일 저장
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to save file to server",
            )

        return file_path

    def remove_temp_file(self, file_path: str):
        """
        S3 업로드가 끝난 후 임시 파일 삭제.
        """
        if os.path.exists(file_path):
            os.remove(file_path)


