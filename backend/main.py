"""
FastAPI Backend — Manufacturing AI Chatbot API

Endpoints:
  POST /api/chat    — Send a message, get AI response
  GET  /api/health  — Health check
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.services.gemini_service import GeminiService


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    tool_used: str | None = None
    session_id: str


# ---------------------------------------------------------------------------
# App lifecycle — validate config on startup
# ---------------------------------------------------------------------------

gemini_service: GeminiService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: validate settings and create the Gemini service."""
    global gemini_service
    settings.validate()
    gemini_service = GeminiService()
    print(f"✅ Backend started | Model: {settings.GEMINI_MODEL}")
    yield
    print("👋 Backend shutting down")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Manufacturing AI Chatbot",
    description="Gemini-powered chatbot with tool calling",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Streamlit (or any frontend) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Simple health check."""
    return {"status": "ok", "model": "This Server uses Gemini API "}

@app.get("/api/server-info")
async def server_info():
    """Get server information."""
    return {
        "Server Name": "Manufacturing AI Chatbot Backend",
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get an AI response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        print(f"✅ got user message sending to gemini AI")
        result = gemini_service.chat(
            message=request.message,
            session_id=request.session_id,
        )
        print(f"✅ Gemini AI returned a response for session: {result.get('session_id', 'N/A')}")
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
