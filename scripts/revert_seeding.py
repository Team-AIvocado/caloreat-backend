import asyncio
import os
import sys
import boto3
from sqlalchemy import text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# 프로젝트 루트를 path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.database import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.prediction_log import PredictionLog
from app.db.models.meal_log import MealLog
from app.core.settings import settings

async def revert_seeding():
    print("seed 스크립트로 생성된 데이터를 모두 삭제합니다..")
    print("S3 버켓 폴더: meals/kfood_dataset/")
    print("유저 이메일: mlops_tester_%@example.com")
    
    confirm = input("진행하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("취소되었습니다.")
        return

    # 1. DB Cleanup
    print("\n[1/3] DB에서 데이터 삭제...")
    async with AsyncSessionLocal() as session:
        # Find Dummy Users
        stmt = select(User.id).where(User.email.like("mlops_tester_%@example.com"))
        result = await session.execute(stmt)
        user_ids = result.scalars().all()
        
        if not user_ids:
            print("DB에 생성된 유저 데이터가 없습니다.")
        else:
            print(f"가상 유저 {len(user_ids)}명을 삭제합니다: {user_ids}")
            
            # Delete PredictionLogs (Explicitly, assuming no FK cascade or to be safe)
            # using DELETE FROM prediction_logs WHERE user_id IN (...)
            await session.execute(
                delete(PredictionLog).where(PredictionLog.user_id.in_(user_ids))
            )
            print(f"가상 유저 {len(user_ids)}명의 PredictionLogs를 삭제했습니다.")
            
            # Delete Users (Should cascade to MealLogs -> MealItems)
            await session.execute(
                delete(User).where(User.id.in_(user_ids))
            )
            print(f"가상 유저 {len(user_ids)}명을 삭제했습니다.")
            
            await session.commit()

    # 2. S3 Cleanup
    print("\n[2/3] S3 버킷에서 데이터 삭제...")
    s3_client = boto3.client(
        "s3", 
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )
    bucket_name = settings.s3_bucket_name
    prefix = "meals/kfood_dataset/"
    
    # List objects
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    delete_keys = []
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                delete_keys.append({'Key': obj['Key']})
    
    if delete_keys:
        print(f"S3 버킷에서 {len(delete_keys)}개의 객체를 삭제합니다.")
        # Delete in batches of 1000 (S3 limit)
        for i in range(0, len(delete_keys), 1000):
            batch = delete_keys[i:i+1000]
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': batch}
            )
            print(f"S3 버킷에서 {i} - {i+len(batch)}번째 객체를 삭제했습니다.")
    else:
        print("S3 버킷에서 삭제할 객체가 없습니다.")

    print("\n[3/3] 복구 완료.")

if __name__ == "__main__":
    asyncio.run(revert_seeding())
