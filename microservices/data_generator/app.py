import os
import sys
import time
import json
import logging
from flask import Flask, jsonify, request
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

SERVICE_NAME   = os.getenv('SERVICE_NAME', 'Data Generator')
KAFKA_BROKERS  = os.getenv('KAFKA_BROKERS', 'localhost:9092')
KAFKA_TOPIC    = os.getenv('KAFKA_TOPIC',   'browser-history')
JSON_PATH      = os.getenv('JSON_PATH',     '/app/history.json')

def make_producer(
    brokers,
    api_version=(2, 8, 0),
    api_version_auto_timeout_ms=30000,
    retries=5,
    backoff=2
):
    for i in range(retries):
        try:
            logger.info(f"Connecting to Kafka at {brokers} (attempt {i+1}/{retries})")
            return KafkaProducer(
                bootstrap_servers=brokers.split(","),
                value_serializer=lambda v: json.dumps(v).encode(),
                api_version=api_version,
                api_version_auto_timeout_ms=api_version_auto_timeout_ms
            )
        except NoBrokersAvailable:
            logger.warning("Kafka broker not ready, retrying in %s seconds…", backoff)
            time.sleep(backoff)
    logger.error("Failed to connect to Kafka after %d attempts", retries)
    sys.exit(1)

producer = make_producer(KAFKA_BROKERS)

@app.route("/")
def health():
    return f"{SERVICE_NAME} is up"

@app.route("/generate", methods=["POST"])
def generate():

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("Browser History")
    if not isinstance(records, list):
        return jsonify({"error": "'Browser History' key missing or not a list"}), 400

    sent = 0
    for entry in records:
        future = producer.send(KAFKA_TOPIC, entry)
        try:
            future.get(timeout=10)
            sent += 1
        except Exception as e:
            logger.error("Failed to send record #%d: %s", sent, e)

    producer.flush()
    return jsonify({
        "status":        "sent",
        "records_total": len(records),
        "records_sent":  sent
    }), 200

if __name__ == "__main__":
    logger.info("Starting %s (Kafka=%s topic=%s JSON=%s)",
                SERVICE_NAME, KAFKA_BROKERS, KAFKA_TOPIC, JSON_PATH)
    app.run(host="0.0.0.0", port=5000, debug=False)
