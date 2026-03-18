# Deploying Mentor AI Chatbot to Google Cloud Run

## Architecture Overview

```
User Browser
     │
     ▼
Cloud Run: mentor-ai-frontend  (Streamlit · port $PORT)
     │  HTTP POST /api/chat
     ▼
Cloud Run: mentor-ai-backend   (FastAPI + Uvicorn · port $PORT)
     │  GEMINI_API_KEY (injected from Secret Manager)
     ▼
Google Gemini API
```

Two independent Cloud Run services are deployed:
| Service | Source | Description |
|---|---|---|
| `mentor-ai-backend` | `backend/Dockerfile` | FastAPI REST API |
| `mentor-ai-frontend` | `frontend/Dockerfile` | Streamlit chat UI |

---

## Feasibility Analysis

### ✅ What Works Well

| Factor | Assessment |
|---|---|
| FastAPI + Uvicorn | Fully Cloud Run compatible — stateless HTTP server |
| Streamlit | Cloud Run compatible — runs as a web server on a single port |
| No persistent disk needed | Sessions are in-memory; no DB or file storage required |
| `requirements.txt` | Clean, minimal dependencies — Docker build is fast |
| `GEMINI_API_KEY` | Injected securely via Cloud Run + Secret Manager |
| CORS set to `["*"]` | No blocker for cross-origin calls between services |

### ⚠️ Considerations

| Issue | Impact | Mitigation |
|---|---|---|
| In-memory session store | Sessions reset on container restart/scale | Acceptable for demo; use Cloud Memorystore (Redis) for production |
| Scale-to-zero cold start | ~1–3s first request latency | Set `--min-instances 1` if low latency is required |
| `BACKEND_URL` was hardcoded | Frontend would fail in cloud | Fixed — now reads from `BACKEND_URL` env var |

### ✅ Verdict: Fully Deployable

---

## Prerequisites

- Google Cloud account with **billing enabled**
- [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed
- Docker Desktop running locally
- A valid `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey)

---

## Step 1 — Authenticate & Configure gcloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Authorize Docker to push to Google Container Registry
gcloud auth configure-docker
```

Replace `YOUR_PROJECT_ID` with your actual GCP project ID.

---

## Step 2 — Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

---

## Step 3 — Store GEMINI_API_KEY in Secret Manager

> Never bake secrets into Docker images or pass them as plain environment variables.

```bash
# Create the secret
echo -n "YOUR_ACTUAL_GEMINI_API_KEY" | \
  gcloud secrets create GEMINI_API_KEY --data-file=-

# Grant Cloud Run's default compute service account access to the secret
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 4 — Code Change — Frontend BACKEND_URL

The file `frontend/app.py` has already been updated to read `BACKEND_URL` from the
environment (with `http://localhost:8000` as the local fallback):

```python
import os
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
```

No manual change needed — this is already applied.

---

## Step 5 — Review Dockerfiles

### `backend/Dockerfile`
```dockerfile
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

### `frontend/Dockerfile`
```dockerfile
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/ ./frontend/
CMD streamlit run frontend/app.py \
    --server.headless true \
    --server.address 0.0.0.0 \
    --server.port ${PORT:-8501}
```

Both files are already created in the repo.

---

## Step 6 — Deploy the Backend

Run from the project root (`MENTOR_AI_CHATBOT/`):

```bash
cd /path/to/MENTOR_AI_CHATBOT

gcloud run deploy mentor-ai-backend \
  --source . \
  --dockerfile backend/Dockerfile \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest" \
  --set-env-vars "GEMINI_MODEL=gemini-2.0-flash" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5
```

When the deployment finishes, **copy the service URL** shown in the output:
```
Service URL: https://mentor-ai-backend-xxxx-uc.a.run.app
```

---

## Step 7 — Deploy the Frontend

Replace `<BACKEND_URL>` with the URL copied in Step 6:

```bash
gcloud run deploy mentor-ai-frontend \
  --source . \
  --dockerfile frontend/Dockerfile \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "BACKEND_URL=https://mentor-ai-backend-xxxx-uc.a.run.app" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3
```

When finished, the frontend URL will be:
```
Service URL: https://mentor-ai-frontend-xxxx-uc.a.run.app
```

---

## Step 8 — Verify Deployment

```bash
# 1. Check backend health endpoint
curl https://mentor-ai-backend-xxxx-uc.a.run.app/api/health
# Expected: {"status":"ok","model":"This Server uses Gemini API "}

# 2. Open the frontend in a browser
open https://mentor-ai-frontend-xxxx-uc.a.run.app
```

---

## Useful Commands

```bash
# View live logs for backend
gcloud run services logs read mentor-ai-backend --region us-central1 --tail 50

# View live logs for frontend
gcloud run services logs read mentor-ai-frontend --region us-central1 --tail 50

# List all deployed Cloud Run services
gcloud run services list --region us-central1

# Delete a service (stop billing)
gcloud run services delete mentor-ai-backend --region us-central1
gcloud run services delete mentor-ai-frontend --region us-central1
```

---

## Cost Estimate

| Resource | Tier | Estimated Cost |
|---|---|---|
| Cloud Run (backend + frontend) | Scale-to-zero | ~$0–2 / month for light usage |
| Cloud Build | First 120 min/day free | $0 for initial deploys |
| Secret Manager | First 6 secret versions free | $0 |
| Artifact Registry | First 0.5 GB free | $0 |

Cloud Run free tier includes **2 million requests/month** and **360,000 GB-seconds** of memory — more than enough for a demo or low-traffic app.

---

## Files Added / Modified

| File | Change |
|---|---|
| `frontend/app.py` | `BACKEND_URL` reads from `os.environ` |
| `backend/Dockerfile` | New — builds FastAPI service |
| `frontend/Dockerfile` | New — builds Streamlit service |
| `.dockerignore` | New — excludes `.env`, `venv/`, caches from image |
| `DEPLOY_CLOUD_RUN.md` | This guide |
