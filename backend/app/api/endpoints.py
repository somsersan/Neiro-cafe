from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.ai_helper import AIAssistant  # Импорт нашего помощника

router = APIRouter()
ai_assistant = AIAssistant()  # Создаем экземпляр помощника

class UserMessage(BaseModel):
    message: str

@router.post("/recommend")
async def get_recommendations(user_input: UserMessage):
    try:
        # Получаем рекомендации от ИИ
        result = ai_assistant.get_recommendations(user_input.message)
        
        return {
            "reply": result["reply"],
            "dishes": result["dishes"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))