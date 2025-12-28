import os
import sys
import boto3
import argparse

# 프로젝트 루트를 path에 추가하여 app 모듈을 찾을 수 있게 함
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

from app.core.settings import settings

def upload_to_s3(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    if not (settings.s3_bucket_name and settings.aws_access_key_id):
        print("Error: AWS credentials or S3 bucket name not configured in settings.")
        return

    print(f"--- Uploading {file_path} to S3 ---")
    s3_client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    filename = os.path.basename(file_path)
    file_key = f"datasets/raw/{filename}"
    bucket_name = settings.s3_bucket_name

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_bytes)
        print(f"S3 업로드 성공: s3://{bucket_name}/{file_key}")
        print("EventBridge로 MLOps pipeline trigger 완료.")
    except Exception as e:
        print(f"S3 업로드 실패: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset CSV to S3.")
    parser.add_argument("file", help="Path to the CSV file to upload")
    args = parser.parse_args()

    upload_to_s3(args.file)
