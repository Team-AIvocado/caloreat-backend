import mimetypes
import logging
import boto3
from botocore.exceptions import ClientError
from app.core.settings import settings

logger = logging.getLogger(__name__)

class S3Client:
    """
    실서비스용 S3 클라이언트.
    -> boto3 Session 재사용
    -> 예외 처리 및 로깅 강화
    -> Content-Type 자동 처리
    -> S3 URL만 반환
    """

    def __init__(self):
        # boto3 Session 기반 생성 (스레드 안전, 재사용 효율)
        self.session = boto3.session.Session(
            aws_access_key_id = settings.aws_access_key_id,
            aws_secret_access_key = settings.aws_secret_access_key,
            region_name = settings.aws_region,
        )

        self.s3 = self.session.client("s3")
        self.bucket = settings.s3_bucket_name
        self.region = settings.aws_region

    def _generate_s3_url(self, object_name: str) -> str:
        """
        Vercel 사용 -> S3 기본 URL만 생성.
        """
        return f"http://{self.bucket}.s3.{self.region}.amazonaws.com/{object_name}"
    
    def upload_file(self, file_path: str, object_name: str, public: bool = True) -> str:
        """
        파일을 S3에 업로드하고 S3 URL을 반환.
        """

        # MIME 타입 자동 추론
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

        extra_args = {"ContentType": content_type}

        # 프론트에서 직접 접근해야 하므로 기본 public-read


        try:
            self.s3.upload_file(
                Filename=file_path,
                Bucket=self.bucket,
                Key=object_name,
                ExtraArgs=extra_args,
            )
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"S3 Upload Error: {str(e)}")
        
        # S3 URL 반환
        return self._generate_s3_url(object_name)
        

