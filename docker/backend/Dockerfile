FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/apps/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash aura

COPY apps/backend /workspace/apps/backend
RUN pip install --upgrade pip && pip install --no-cache-dir -e .

USER aura

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --fail http://127.0.0.1:8000/api/v1/health || exit 1

CMD ["uvicorn", "aura_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
