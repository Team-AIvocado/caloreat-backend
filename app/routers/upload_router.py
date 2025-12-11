from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload_service import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

upload_service = UploadService()

@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드하여 S3 URL을 반환하는 API.

    요청 형식:
    - multipart/form-data
    - file: UploadFile

    응답 형식:
    {
        "url": "https://s3-bucket.amazonaws.com/uploads/uuid.png"
    }
    """

    # 이미지 업로드 처리
    try:
        url = upload_service.upload_image(file)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Image upload failed")
    
    return {"url": url}