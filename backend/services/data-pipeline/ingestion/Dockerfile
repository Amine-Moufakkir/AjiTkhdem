FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN groupadd -r kafkauser && useradd -r -g kafkauser kafkauser

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# FIX: Tell Python that /app is the root directory for imports
ENV PYTHONPATH="/app"

COPY . .

EXPOSE 8000

RUN chown -R kafkauser:kafkauser /app /opt/venv

USER kafkauser

CMD ["python", "src/main.py"]