from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_assistant import AIAssistant

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или укажи конкретные адреса, например ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = AIAssistant()

class UserRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: UserRequest):
    try:
        # Получаем рекомендации от помощника
        result = assistant.get_recommendations(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)