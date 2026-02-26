# Mentor AI Chatbot — Architecture Document

## 1. Current State Analysis

### What We Have
A **single-file CLI script** (`gemini_chat_tool_calling.py`) that:
- Connects to Gemini API with tool/function calling
- Defines a `get_current_time` tool
- Runs an interactive `input()` loop in the terminal
- Maintains conversation history in a Python list (in-memory)

### Limitations
| Problem | Impact |
|---|---|
| CLI only — no web interface | Not shareable, no UI |
| No separation of concerns | Business logic mixed with I/O |
| Single user, single session | No concurrent usage |
| No persistence | History lost on restart |
| Hard to extend | Adding tools requires editing one big file |

---

## 2. Target Architecture (Keep It Simple)

### Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend API** | **FastAPI** (Python) | Async, lightweight, auto-generated docs, perfect for AI APIs |
| **Frontend UI** | **Streamlit** (Python) | Rapid chat UI with zero JS, built-in chat components |
| **AI SDK** | `google-genai` | Already in use — no change needed |

### Why These Choices?
- **Both are Python** — single language, single `requirements.txt`
- **FastAPI** is the standard for Python AI backends (async, fast, typed)
- **Streamlit** has built-in `st.chat_message` / `st.chat_input` — a chat UI in ~50 lines
- **No JS/HTML/CSS needed** — the user asked for Python frameworks on both sides

---

## 3. Project Structure

```
MENTOR_AI_CHATBOT/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Settings & API key management
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py       # Tool registry (maps names → functions)
│   │   └── time_tool.py      # get_current_time tool
│   └── services/
│       ├── __init__.py
│       └── gemini_service.py # Gemini API interaction logic
├── frontend/
│   └── app.py                # Streamlit chat UI
├── requirements.txt
├── README.md
└── ARCHITECTURE.md           # This file
```

---

## 4. Component Design

### 4.1 Backend (FastAPI)

#### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/chat` | Send a message, get AI response |
| `GET` | `/api/health` | Health check |

#### `/api/chat` — Request/Response

**Request:**
```json
{
  "message": "What time is it?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "It's currently Tuesday, February 26, 2026 at 2:30 PM IST.",
  "tool_used": "get_current_time",
  "session_id": "abc123"
}
```

#### Key Design Decisions
- **Session-based conversation history** stored in a simple in-memory dict (keyed by `session_id`)
- **Tool registry pattern** — tools are registered in a dict, easy to add new ones
- **Gemini service** is a separate class — testable, swappable

### 4.2 Frontend (Streamlit)

#### Features
- Chat-style UI using `st.chat_message` and `st.chat_input`
- Conversation history displayed in chat bubbles
- Shows when a tool is being called (expandable section)
- Calls backend API via `requests` library
- Session state managed by Streamlit's `st.session_state`

#### UI Flow
```
┌─────────────────────────────────┐
│  🤖 Mentor AI Chatbot           │
├─────────────────────────────────┤
│                                 │
│  👤 What time is it?            │
│                                 │
│  🤖 It's Tuesday, Feb 26,      │
│     2026 at 2:30 PM IST.       │
│     ▸ Tool used: get_current_   │
│       time                      │
│                                 │
│  👤 Tell me a joke              │
│                                 │
│  🤖 Why do programmers prefer   │
│     dark mode? ...              │
│                                 │
├─────────────────────────────────┤
│  Type your message...     [Send]│
└─────────────────────────────────┘
```

---

## 5. Data Flow

```
User types message in Streamlit UI
        │
        ▼
Streamlit sends POST /api/chat
        │
        ▼
FastAPI receives request
        │
        ▼
GeminiService builds conversation context
        │
        ▼
Calls Gemini API with tools config
        │
        ▼
Gemini responds → tool call needed?
    ├── NO  → return text response directly
    └── YES → ToolRegistry executes the tool locally
                  │
                  ▼
              Send tool result back to Gemini
                  │
                  ▼
              Gemini returns final text
        │
        ▼
FastAPI returns JSON response
        │
        ▼
Streamlit displays in chat bubble
```

---

## 6. How to Add a New Tool (Extensibility)

Adding a new tool requires only **2 steps**:

### Step 1: Create the tool file
```python
# backend/tools/weather_tool.py

DECLARATION = {
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"}
        },
        "required": ["city"],
    },
}

def execute(city: str) -> dict:
    # Your implementation here
    return {"city": city, "temp": "25°C", "condition": "Sunny"}
```

### Step 2: Register it
```python
# backend/tools/registry.py
from backend.tools import time_tool, weather_tool

TOOLS = {
    "get_current_time": time_tool,
    "get_weather": weather_tool,
}
```

That's it — the backend auto-discovers declarations and functions from the registry.

---

## 7. Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start the backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start the frontend
streamlit run frontend/app.py
```

- Backend API docs: http://localhost:8000/docs
- Frontend UI: http://localhost:8501

---

## 8. Future Enhancements (Out of Scope for Now)

| Enhancement | Description |
|---|---|
| Database persistence | Store chat history in SQLite/PostgreSQL |
| Authentication | User login via OAuth |
| Streaming responses | SSE/WebSocket for token-by-token streaming |
| More tools | Web search, calculator, file reader, etc. |
| Docker deployment | Containerize both services |
| Testing | Unit tests for tools, integration tests for API |

---

## 9. Dependencies

```
# requirements.txt
fastapi>=0.115.0
uvicorn>=0.34.0
google-genai>=1.0.0
streamlit>=1.41.0
requests>=2.32.0
pydantic>=2.10.0
```
