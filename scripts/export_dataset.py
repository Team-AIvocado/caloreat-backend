import asyncio
import os
import sys
import csv
import json
from datetime import datetime
from sqlalchemy import text

# 프로젝트 루트를 path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.database import AsyncSessionLocal

async def export_dataset():
    print("Start exporting dataset from DB...")
    
    # OUTPUT FILE NAME
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dataset_{timestamp}.csv"
    
    query = text("""
        SELECT 
            pl.image_id,
            pl.model_version,
            pl.raw_response,
            m.image_urls,
            mi.foodname as ground_truth,
            pl.created_at
        FROM prediction_logs pl
        JOIN meal_logs m ON m.image_urls::text LIKE '%' || pl.image_id || '%'
        JOIN meal_items mi ON mi.meal_log_id = m.id
        ORDER BY pl.id DESC
    """)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(query)
        rows = result.fetchall()
        
    print(f"Found {len(rows)} records. Writing to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['image_id', 'ground_truth', 'prediction', 'confidence', 'is_correct', 'model_version', 's3_url', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        count_correct = 0
        
        for row in rows:
            # Parse Raw Response (JSON)
            raw_res = row.raw_response
            if isinstance(raw_res, str):
                raw_res = json.loads(raw_res)
                
            # Handle different response structures if needed (e.g. error case)
            if 'food_name' in raw_res:
                prediction = raw_res['food_name']
                # Confidence might be in 'confidence' or inside 'candidates'
                confidence = raw_res.get('confidence', 0.0)
                # If confidence is low/missing, check candidates
                if confidence == 0.0 and 'candidates' in raw_res and raw_res['candidates']:
                    confidence = raw_res['candidates'][0].get('confidence', 0.0)
            else:
                prediction = "Error/Unknown"
                confidence = 0.0
                
            ground_truth = row.ground_truth
            is_correct = (prediction == ground_truth)
            if is_correct:
                count_correct += 1
            
            # Extract S3 URL
            # image_urls is JSON array: ["https://..."]
            s3_url = ""
            image_urls = row.image_urls
            if isinstance(image_urls, str): # if stored as string
                try:
                    image_urls = json.loads(image_urls)
                except:
                    pass
            
            if isinstance(image_urls, list) and image_urls:
                s3_url = image_urls[0]

            writer.writerow({
                'image_id': row.image_id,
                'ground_truth': ground_truth,
                'prediction': prediction,
                'confidence': f"{confidence:.4f}",
                'is_correct': is_correct,
                'model_version': row.model_version,
                's3_url': s3_url,
                'created_at': row.created_at
            })
            
    print(f"Done! Saved to {filename}")
    if len(rows) > 0:
        print(f"Accuracy: {count_correct / len(rows) * 100:.2f}% ({count_correct}/{len(rows)})")

if __name__ == "__main__":
    asyncio.run(export_dataset())
