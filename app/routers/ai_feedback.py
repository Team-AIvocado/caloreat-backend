from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.schemas.ai_feedback import AIFeedbackRequest, AIFeedbackResponse
from app.services.ai_feedback import AIFeedbackService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/feedback", response_model=AIFeedbackResponse)
async def submit_ai_feedback(
    feedback: AIFeedbackRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "feedback accepted"}
    # return await AIFeedbackService.submit(feedback)
