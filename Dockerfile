FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

#Set Environment Variables for Offline mode
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY models/ models/
COPY batch_run.py round1b_offline.py ./
COPY case1/ case1/
COPY case2/ case2/
COPY case3/ case3/

RUN mkdir -p /app/case1/output /app/case2/output /app/case3/output

CMD ["python", "batch_run.py"]
