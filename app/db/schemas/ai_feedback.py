from pydantic import BaseModel


class AIFeedbackRequest(BaseModel):
    image_id: str
    correct_food: str


class AIFeedbackResponse(BaseModel):
    message: str = "feedback accepted"
