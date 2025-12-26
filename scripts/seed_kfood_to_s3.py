import os
import argparse
import asyncio
import random
import uuid
import sys
import zipfile
import mimetypes
import boto3
import shutil
import httpx
import json
import io
from datetime import datetime, timezone


# --- [FIX] Monkeypatch for BadZipFile: Corrupt extra field ---
def _decodeExtra(self, *args):
    pass


zipfile.ZipInfo._decodeExtra = _decodeExtra
# -------------------------------------------------------------

# 프로젝트 루트를 path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# DB 관련 import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import AsyncSessionLocal
from app.db.models.prediction_log import PredictionLog
from app.db.models.meal_log import MealLog
from app.db.models.meal_item import MealItem
from app.db.models.user import User
from app.core.settings import settings

# 랜덤 시드
random.seed(42)

# S3 Client (Standalone using boto3 directly)
s3_client = boto3.client(
    "s3",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
bucket_name = settings.s3_bucket_name


def upload_to_s3(file_obj, object_name: str, content_type: str) -> str:
    """Stream upload directly to S3"""
    try:
        s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=bucket_name,
            Key=object_name,
            ExtraArgs={"ContentType": content_type},
        )
        # Assuming public access or using as internal URL reference
        return f"https://{bucket_name}.s3.{settings.aws_region}.amazonaws.com/{object_name}"
    except Exception as e:
        print(f"[S3 Error] {e}")
        return None


async def request_ai_inference(
    image_bytes: bytes, image_id: str, content_type: str, ai_url: str
) -> dict:
    """
    Send image to AI service for real inference
    POST /api/inference/v4/analyze
    """
    try:
        filename = "image.png" if content_type == "image/png" else "image.jpg"
        files = {"image": (filename, image_bytes, content_type)}
        data = {"image_id": image_id}

        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            target_url = f"{ai_url.rstrip('/')}/api/inference/v4/analyze"
            response = await client.post(target_url, data=data, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[AI Error] Inference failed: {e}")
        return {"error": str(e), "food_name": "AI_Error_Fallback", "confidence": 0.0}


async def get_or_create_dummy_users(session: AsyncSession, count: int = 5) -> list[int]:
    """
    여러 명의 더미 유저를 확보하여 리스트로 반환
    """
    user_ids = []

    # 기존 더미 유저 확인
    result = await session.execute(
        text("SELECT id FROM users WHERE email LIKE 'mlops_tester_%@example.com'")
    )
    existing_ids = result.scalars().all()
    user_ids.extend(existing_ids)

    # 부족하면 추가 생성
    needed = count - len(user_ids)
    if needed > 0:
        print(f"[Info] Creating {needed} additional dummy users...")
        for i in range(needed):
            idx = len(user_ids) + 1 + i  # simple index
            email = f"mlops_tester_{idx}_{uuid.uuid4().hex[:4]}@example.com"
            new_user = User(
                email=email,
                username=f"tester_{idx}_{uuid.uuid4().hex[:4]}",
                password="dummy_password",
                nickname=f"Tester_{idx}",
                is_active=True,
            )
            session.add(new_user)
            await session.flush()
            user_ids.append(new_user.id)

        await session.commit()

    return user_ids


async def process_inner_zip(
    inner_zip_path: str,
    max_images_per_zip: int,
    session: AsyncSession,
    user_ids: list[int],
    ai_url: str,
):
    """
    내부 zip 파일(예: 김치.zip)을 열어서 이미지 처리
    """
    processed_count = 0

    try:
        with zipfile.ZipFile(inner_zip_path, "r") as z:
            file_list = z.namelist()
            image_files = [
                f
                for f in file_list
                if f.lower().endswith((".jpg", ".jpeg", ".png")) and "__MACOSX" not in f
            ]
            random.shuffle(image_files)

            for file_path in image_files:
                if processed_count >= max_images_per_zip:
                    break

                parts = file_path.split("/")
                if len(parts) > 1:
                    food_name = parts[-2]
                else:
                    food_name = os.path.basename(inner_zip_path).replace(".zip", "")

                if not food_name:
                    continue

                current_user_id = random.choice(user_ids)

                filename = os.path.basename(file_path)
                image_uuid = str(uuid.uuid4())
                ext = os.path.splitext(filename)[1].lower()
                content_type = (
                    mimetypes.guess_type(filename)[0] or "application/octet-stream"
                )

                # S3 Key
                object_name = f"meals/kfood_dataset/{food_name}/{image_uuid}{ext}"

                print(
                    f"   -> Processing {food_name}: {filename} (User: {current_user_id})"
                )

                # Read File Bytes ONCE
                with z.open(file_path) as source_file:
                    file_bytes = source_file.read()

                # 1. S3 Upload (using BytesIO)
                s3_url = upload_to_s3(io.BytesIO(file_bytes), object_name, content_type)

                if not s3_url:
                    continue

                # 2. Real AI Inference
                ai_response = await request_ai_inference(
                    file_bytes, image_uuid, content_type, ai_url
                )

                # PredictionLog
                pl = PredictionLog(
                    image_id=image_uuid,
                    user_id=current_user_id,
                    raw_response=ai_response,  # SAVE REAL RESPONSE
                    model_version="v4-real",
                )
                session.add(pl)

                # MealLog (Ground Truth)
                ml = MealLog(
                    user_id=current_user_id,
                    meal_type="Lunch",
                    eaten_at=datetime.now(timezone.utc),
                    image_urls=[s3_url],
                )
                # MealItem
                mi = MealItem(foodname=food_name, quantity=1.0, nutritions={})
                ml.meal_items.append(mi)
                session.add(ml)

                await session.commit()
                processed_count += 1

    except zipfile.BadZipFile:
        print(f"   [Error] Bad zip file: {inner_zip_path}")
    except Exception as e:
        print(f"   [Error] Processing inner zip failed: {e}")

    return processed_count


async def seed_from_nested_zip(
    root_zip_path: str, max_images_total: int, ai_url: str, dry_run: bool = False
):
    """
    메인 로직: Root Zip -> Extract Inner Zip -> Process -> Delete Inner Zip
    """
    if dry_run:
        print("[Info] DRY RUN MODE - S3 Upload/DB Insert/AI Request skipped.")

    temp_dir = "temp_seed_extract_retry"
    os.makedirs(temp_dir, exist_ok=True)

    total_processed = 0

    async with AsyncSessionLocal() as session:
        if not dry_run:
            user_ids = await get_or_create_dummy_users(session, count=5)
        else:
            user_ids = [0]

        with zipfile.ZipFile(root_zip_path, "r") as root_z:
            inner_zips = [f for f in root_z.namelist() if f.lower().endswith(".zip")]
            print(f"[Info] Found {len(inner_zips)} category zip files.")

            if not inner_zips:
                print("[Warning] No inner zip files found.")
                shutil.rmtree(temp_dir)
                return

            limit_per_zip = max(1, max_images_total // len(inner_zips))
            print(f"[Info] Target images per category: {limit_per_zip}")

            for inner_zip_name in inner_zips:
                if total_processed >= max_images_total:
                    break

                # [FIX] Handle Korean Filenames (CP437 -> CP949)
                try:
                    raw_name = inner_zip_name.encode("cp437")
                    decoded_name = raw_name.decode("cp949")
                except:
                    decoded_name = inner_zip_name

                print(f"[Processing Category] {decoded_name} ...")

                extract_path = os.path.join(temp_dir, decoded_name)
                os.makedirs(os.path.dirname(extract_path), exist_ok=True)

                with root_z.open(inner_zip_name) as zf, open(extract_path, "wb") as f:
                    shutil.copyfileobj(zf, f)

                if not dry_run:
                    count = await process_inner_zip(
                        extract_path, limit_per_zip, session, user_ids, ai_url
                    )
                    total_processed += count
                else:
                    print(
                        f"   [Dry Run] Extracted {inner_zip_name}, would process ~{limit_per_zip} images."
                    )

                os.remove(extract_path)

    shutil.rmtree(temp_dir)
    print(f"[Done] Total {total_processed} images seeded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", required=True)
    parser.add_argument("--max-images", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    # AI Service URL Default
    parser.add_argument(
        "--ai-url", default="http://localhost:8001", help="AI Service Base URL"
    )
    args = parser.parse_args()

    if not os.path.exists(args.zip_path):
        print(f"File not found: {args.zip_path}")
        sys.exit(1)

    asyncio.run(
        seed_from_nested_zip(args.zip_path, args.max_images, args.ai_url, args.dry_run)
    )
