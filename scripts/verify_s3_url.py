import asyncio
import sys
import os
from sqlalchemy import text # Added import

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.database import AsyncSessionLocal

import boto3
from app.core.settings import settings

async def check_last_url():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT image_urls FROM meal_logs ORDER BY id DESC LIMIT 1"))
        url_json = result.scalar()
        
        if url_json:
            stored_url = url_json[0]
            print(f"\n[Stored URL] {stored_url}")
            
            # Extract Object Key from URL
            # Format: https://{bucket}.s3.{region}.amazonaws.com/{key}
            try:
                # Split by amazonaws.com/ to get the key
                key = stored_url.split(".amazonaws.com/")[-1]
                
                # Generate Presigned URL
                s3_client = boto3.client(
                    "s3",
                    region_name=settings.aws_region,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                )
                
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.s3_bucket_name, 'Key': key},
                    ExpiresIn=3600
                )
                
                print(f"[Presigned URL] (Valid for 1 hour):")
                print(presigned_url)
                print("\nClick the [Presigned URL] above to verify.")
                
            except Exception as e:
                print(f"Failed to generate presigned URL: {e}")
                
        else:
            print("No meal logs found.")

if __name__ == "__main__":
    asyncio.run(check_last_url())
