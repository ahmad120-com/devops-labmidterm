# Stage 1: Python + ML libraries (cached, so retraining is fast)
FROM python:3.11-slim AS deps
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest httpx

# Stage 2: app + freshly trained model
FROM deps AS app
COPY app.py train.py config.json ./
COPY artifacts/ artifacts/
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
