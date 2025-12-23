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

    # presigned url 생성(S3요청 boto3)
    @classmethod
    def generate_presigned_url(cls, object_name: str, expiration: int = 3600) -> str:
        """
        Private S3 객체에 접근 가능한 Presigned URL 생성
        """
        try:
            response = cls._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": cls._bucket, "Key": object_name},
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            logger.error(f"S3 presigned url generation failed: {e}")
            return ""

    # DB저장된 image_url을 presigned url로 변환
    @classmethod
    def convert_to_presigned_url(cls, original_url: str) -> str:
        """
        기존 Full URL을 파싱하여 Presigned URL로 변환
        - Key 추출 로직 포함 (Infrastructure Responsibility)
        """
        if not original_url:
            return original_url

        try:
            # Extract Key from URL
            # Assumption: URL ends with /ObjectKey (Simple logic for now)
            # e.g., https://bucket.../meals/uuid.jpg -> meals/uuid.jpg
            # TODO: 추후 URL 파싱 로직 강화 (urllib.parse 등 활용)
            key = "/".join(original_url.split("/")[-2:])

            signed_url = cls.generate_presigned_url(key)
            return signed_url if signed_url else original_url
        except Exception as e:
            logger.warning(f"Failed to convert url: {original_url}, error: {e}")
            return original_url
