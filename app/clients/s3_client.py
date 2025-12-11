import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
from typing import Optional
from app.core.settings import settings

# dabin or use this skeleton


class S3Client:
    """
    AWS S3와의 통신을 담당하는 클라이언트
    이미지 업로드, 삭제 등의 기능을 제공
    """

    # Boto3 클라이언트 생성 (class level or instance level)
    # s3_client = boto3.client(
    #     's3',
    #     aws_access_key_id=settings.aws_access_key_id,
    #     aws_secret_access_key=settings.aws_secret_access_key,
    #     region_name=settings.aws_region
    # )

    @staticmethod
    def upload_file(
        file: UploadFile, object_name: Optional[str] = None
    ) -> Optional[str]:
        """
        파일을 S3 버킷에 업로드하고 URL을 반환
        """
        # 1. 파일 포인터 초기화
        # await file.seek(0) (FastAPI UploadFile은 비동기 메서드 지원하므로 주의, boto3는 동기 라이브러리임)
        # Boto3의 upload_fileobj는 file-like object를 받음. file.file이 file-like임.

        # 2. 파일명 결정
        # object_name이 없으면 file.filename 사용

        # 3. S3 업로드
        # try:
        #     s3_client.upload_fileobj(
        #         file.file,
        #         settings.s3_bucket_name,
        #         object_name,
        #         ExtraArgs={"ContentType": file.content_type}
        #     )
        # except NoCredentialsError:
        #     # 자격 증명 오류 처리
        #     return None

        # 4. URL 생성 및 반환
        # url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{object_name}"
        # return url
        pass

    @staticmethod
    def delete_file(object_name: str):
        """
        S3 버킷에서 파일 삭제
        """
        # 1. S3 삭제 요청
        # try:
        #     s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=object_name)
        # except Exception as e:
        #     # 로깅 및 에러 처리
        #     raise e
        pass

#