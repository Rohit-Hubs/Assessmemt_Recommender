from fastapi import APIRouter
from agent.models import ChatRequest, ChatResponse
from agent.chat_agent import generate_chat_response

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    return generate_chat_response(request)
