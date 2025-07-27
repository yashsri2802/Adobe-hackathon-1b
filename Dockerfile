FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY models/ /app/models/
COPY batch_run.py round1b_offline.py ./
COPY case1/ /app/case1/
COPY case2/ /app/case2/
COPY case3/ /app/case3/

RUN mkdir -p /app/case1/output /app/case2/output /app/case3/output

CMD ["python", "batch_run.py"]
