from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException

from src.agent.graph_builder import BotPipeline


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = {}

    def get(self, sid: str) -> List[Dict]:
        return self.sessions.get(sid, [])

    def set(self, sid: str, history: List[Dict]):
        self.sessions[sid] = history

    def create(self) -> str:
        sid = str(uuid4())
        self.sessions[sid] = []
        return sid

# session_store = SessionStore()



# In-memory store (replace with Redis for prod)
_sessions: Dict[str, BotPipeline] = {}

app = FastAPI(title="Intent-Routed Agent API")

def get_pipeline(session_id: str) -> BotPipeline:
    """Get or create BotPipeline per session."""
    if session_id not in _sessions:
        pipeline = BotPipeline()
        pipeline.build_graph()  # Build graph once per session
        _sessions[session_id] = pipeline
    return _sessions[session_id]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    sid = request.session_id or str(uuid4())

    pipeline = get_pipeline(sid)

    try:
        answer = pipeline.execute_graph(
            query=request.message,
            thread_id=sid
        )

        return ChatResponse(
            session_id=sid,
            answer=answer,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/")
async def root():
    return {
        "status": "agent ready",
        "active_sessions": len(_sessions)
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]
        return {"detail": "Session cleared"}
    return {"detail": "Session not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",   
        host="0.0.0.0",
        port=8000,
        reload=True      
    )