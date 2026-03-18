# ── Backend Dockerfile ───────────────────────────────────────────────────────
# Builds the FastAPI + Uvicorn service.
# Cloud Run injects $PORT (default 8080); we read it in the CMD.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# Keep Python output unbuffered so logs appear in Cloud Logging immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend/ ./backend/

# Cloud Run sets $PORT; uvicorn binds to it
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
