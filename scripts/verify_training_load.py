import csv
import boto3
import os
import sys
import glob
import random
from io import BytesIO
from PIL import Image

# 프로젝트 루트를 path에 추가 (settings 사용 위함)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.core.settings import settings

def verify_training_load(sample_size=10):
    # 1. 최신 CSV 찾기
    list_of_files = glob.glob('dataset_*.csv') 
    if not list_of_files:
        print("No dataset CSV found!")
        return
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"[Info] Loading dataset from: {latest_file}")

    # 2. CSV 읽기 (using csv module instead of pandas)
    data = []
    with open(latest_file, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            
    print(f"[Info] Total records: {len(data)}")
    
    # 3. 샘플링
    if len(data) > sample_size:
        sample = random.sample(data, sample_size)
    else:
        sample = data
        
    print(f"[Info] Verifying {len(sample)} images...")

    # S3 Client
    s3_client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    success_count = 0
    
    for i, row in enumerate(sample):
        s3_url = row['s3_url']
        # Progress (Simple print)
        print(f"[{i+1}/{len(sample)}] Checking {s3_url} ... ", end="")
        
        try:
            # URL에서 Key 추출
            if not s3_url:
                print("Skipped (No URL)")
                continue

            # https://{bucket}.s3.{region}.amazonaws.com/{key}
            key = s3_url.split(".amazonaws.com/")[-1]
            
            # 다운로드 (Memory)
            obj = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=key)
            img_data = obj['Body'].read()
            
            # 이미지 무결성 확인
            image = Image.open(BytesIO(img_data))
            image.verify() # 손상 여부 확인
            
            print("OK")
            success_count += 1
            
        except Exception as e:
            print(f"Failed ({e})")

    print(f"\n[Result] Successfully loaded {success_count}/{len(sample)} images.")
    
    if success_count == len(sample):
        print("훈련 데이터 준비 완료.")
    else:
        print("이미지 로딩 실패. 검증 필요")

if __name__ == "__main__":
    verify_training_load()
