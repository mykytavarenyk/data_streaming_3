FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc \
      librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

COPY app.py .

RUN pip install --no-cache-dir \
      quixstreams

CMD ["python", "app.py"]
