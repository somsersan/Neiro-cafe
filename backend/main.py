from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_assistant import AIAssistant
import random
from collections import defaultdict
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = AIAssistant()

class UserRequest(BaseModel):
    message: str

class VoteRequest(BaseModel):
    session_id: str
    selected_model: str  # "model_1" или "model_2"

vote_stats = defaultdict(int)
response_cache = {}

def get_leader() -> dict:
    """Определение модели-лидера на основе статистики голосов"""
    if not vote_stats:
        return {"leader": None, "message": "No votes yet"}
    
    # Находим максимальное количество голосов
    max_votes = max(vote_stats.values())
    
    # Находим все модели с максимальным количеством голосов
    leaders = [model for model, votes in vote_stats.items() if votes == max_votes]
    
    # Формируем результат
    result = {
        "total_votes": sum(vote_stats.values()),
        "max_votes": max_votes,
        "models": {model: vote_stats[model] for model in vote_stats}
    }
    
    if len(leaders) == 1:
        result["leader"] = leaders[0]
    else:
        result["leader"] = "tie"
        result["tied_models"] = leaders
    
    return result

@app.post("/chat")
async def chat(request: UserRequest):
    try:
        result = assistant.get_recommendations(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sbs/chat")
async def sbs_chat(request: UserRequest):
    try:
        session_id = str(uuid.uuid4())
        responses = assistant.get_dual_responses(request.message)
        
        models = ["gigachat", "yandexgpt"]
        random.shuffle(models)
        
        response_cache[session_id] = {
            "model_1": models[0],
            "model_2": models[1],
            "responses": responses
        }
        
        return {
            "session_id": session_id,
            "response_1": responses[models[0]]["reply"],
            "response_2": responses[models[1]]["reply"],
            "dishes": responses[models[0]]["dishes"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sbs/vote")
async def sbs_vote(request: VoteRequest):
    if request.session_id not in response_cache:
        raise HTTPException(status_code=404, detail="Session not found")
    
    vote_stats[request.selected_model] += 1
    return {"status": "vote counted"}

@app.get("/sbs/stats")
async def get_sbs_stats():
    # Возвращаем полную статистику с определением лидера
    return get_leader()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)