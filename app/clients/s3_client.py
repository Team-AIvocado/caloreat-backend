import mimetypes
import logging
import boto3
from botocore.exceptions import ClientError
from app.core.settings import settings

logger = logging.getLogger(__name__)

# TODO: 추후 트래픽 증가시 upload_file 내부 로직에 run_in_threadpool 적용 고려 (Non-blocking I/O)


class S3Client:
    """
    AWS S3 Client (Static Interface)
    - 책임: S3 업로드/삭제 (인프라 계층)
    - 특징: MealImageService에서 static하게 호출 가능하도록 설계
    """

    # Boto3 Client (Lazy loading or Module level)
    # IAM Role(ECS) 지원을 위해 동적으로 자격증명 처리
    _client_kwargs = {"region_name": settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        _client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        _client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    _client = boto3.client("s3", **_client_kwargs)
    _bucket = settings.s3_bucket_name
    _region = settings.aws_region

    @classmethod
    def _generate_s3_url(cls, object_name: str) -> str:
        return f"https://{cls._bucket}.s3.{cls._region}.amazonaws.com/{object_name}"

    @classmethod
    def upload_file(cls, file_path: str, object_name: str) -> str:
        """
        파일을 S3에 업로드하고 S3 URL을 반환 (Static/Class Method)
        """
        # MIME 타입 추론
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"

        extra_args = {"ContentType": content_type}

        try:
            cls._client.upload_file(
                Filename=file_path,
                Bucket=cls._bucket,
                Key=object_name,
                ExtraArgs=extra_args,
            )
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"S3 Upload Error: {str(e)}")

        return cls._generate_s3_url(object_name)

    @staticmethod
    def delete_file(object_name: str):
        """
        S3 버킷에서 파일 삭제 (Admin)
        """
        try:
            # 클래스 변수 접근을 위해 S3Client._client 사용
            S3Client._client.delete_object(Bucket=S3Client._bucket, Key=object_name)
        except ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            # 필요 시 raise
            pass
