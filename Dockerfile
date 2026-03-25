# ── Backend stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generate_data.py clean_data.py analyze.py ./
COPY backend/ ./backend/
COPY data/ ./data/

ENV DATA_DIR=/app/data/processed
ENV FRONTEND_DIR=/app/frontend/dist

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
