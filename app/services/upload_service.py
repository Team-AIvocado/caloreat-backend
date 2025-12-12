import logging
from app.clients.s3_client import S3Client
from app.services.file_manager import FileManager
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class UploadService:
    """
    이미지 업로드 전체 흐름을 관리하는 실서비스용 서비스 클래스.

    흐름:
    1. UploadFile 검증 및 임시 저장
    2. S3 업로드
    3. 임시 파일 삭제
    4. S3 URL 반환
    """

    def __init__(self):
        self.file_manager = FileManager()
        self.s3_client = S3Client()

    def upload_image(self, file: UploadFile) -> str:
        """
        이미지 파일을 받아 S3에 업로드 후 URL을 반환.

        모든 과정에서 실패 시 적절한 HTTPException 발생시킴.
        """

        # 임시 저장
        try:
            temp_path = self.file_manager.save_temp_file(file)
        except HTTPException as e:
            # FileManager에서 검증 실패하면 그대로 전달
            raise e
        except Exception as e:
            logger.error(f"[UploadService] Temp file save failed: {e}")
            raise HTTPException(status_code=500, detail="Internal file processing error")
        
        # S3 업로드
        object_name = f"uploads/{temp_path.split('/')[-1]}"
        # S3 내부 폴더 구조 -> uploads/uuid.png

        try:
            s3_url = self.s3_client.upload_file(
                file_path=temp_path,
                object_name=object_name,
                public=True,
            )
        except Exception as e:
            logger.error(f"[UploadService] S3 upload failed: {e}")
            raise HTTPException(status_code=500, detail="S3 upload failed")
        
        # 임시 파일 삭제
        try:
            self.file_manager.remove_temp_file(temp_path)
        except Exception as e:
            logger.warning(f"[UploadService] Temp file cleanup failed: {e}")
            # 파일 삭제 실패는 치명적이지 않으므로 서비스 중단까지 이어지지 않음

        return s3_url
