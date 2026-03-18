# Mentor AI Chatbot — GCP Cloud Run Architecture

## High-Level Diagram

```mermaid
graph TB
    subgraph User["👤 User"]
        Browser["Web Browser"]
    end

    subgraph GCP["Google Cloud Platform"]
        subgraph CR_Frontend["Cloud Run: mentor-ai-frontend"]
            Streamlit["Streamlit App<br/>(frontend/app.py)<br/>Port: 8501"]
        end

        subgraph CR_Backend["Cloud Run: mentor-ai-backend"]
            FastAPI["FastAPI + Uvicorn<br/>(backend/main.py)<br/>Port: 8000"]
        end

        subgraph SecretMgr["Secret Manager"]
            APIKey["GEMINI_API_KEY"]
        end
    end

    subgraph Google["Google AI"]
        Gemini["Gemini API<br/>(gemini-2.0-flash)"]
    end

    Browser -- "HTTPS<br/>User opens chat UI" --> Streamlit
    Streamlit -- "POST /api/chat<br/>HTTPS (internal)<br/>via BACKEND_URL env var" --> FastAPI
    FastAPI -- "Read secret<br/>on startup" --> APIKey
    FastAPI -- "generate_content()<br/>with tool declarations" --> Gemini
    Gemini -- "Response / Tool Call" --> FastAPI
    FastAPI -- "JSON Response<br/>{response, tool_used, session_id}" --> Streamlit
    Streamlit -- "Rendered Chat UI" --> Browser

    style GCP fill:#e8f0fe,stroke:#4285f4,stroke-width:2px
    style CR_Frontend fill:#e6f4ea,stroke:#34a853,stroke-width:2px
    style CR_Backend fill:#fce8e6,stroke:#ea4335,stroke-width:2px
    style SecretMgr fill:#fef7e0,stroke:#fbbc04,stroke-width:2px
    style Google fill:#f3e8fd,stroke:#a142f4,stroke-width:2px
```

## Flow Summary

1. **User** opens the Streamlit frontend URL in their browser
2. **Streamlit** (Cloud Run #1) renders the chat UI and sends user messages via `POST /api/chat` to the backend using the `BACKEND_URL` env var
3. **FastAPI** (Cloud Run #2) receives the request, loads `GEMINI_API_KEY` from Secret Manager, and calls the Gemini API with tool declarations
4. **Gemini** processes the message (optionally executing tool calls like `get_current_time`) and returns a response
5. **FastAPI** sends the JSON response back to Streamlit, which renders it in the chat UI
