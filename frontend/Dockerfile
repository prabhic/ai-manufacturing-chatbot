# ── Frontend Dockerfile ──────────────────────────────────────────────────────
# Builds the Streamlit UI service.
# Cloud Run injects $PORT; Streamlit must bind to it explicitly.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source
COPY frontend/ ./frontend/

# Streamlit requires these flags to run headlessly on Cloud Run:
#   --server.headless true        → disables "open in browser" prompt
#   --server.address 0.0.0.0      → bind to all interfaces
#   --server.port $PORT           → use Cloud Run's dynamic port
#   --server.enableCORS false     → not needed since backend is separate
CMD streamlit run frontend/app.py \
    --server.headless true \
    --server.address 0.0.0.0 \
    --server.port ${PORT:-8501}
