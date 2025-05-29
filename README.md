# data\_streaming\_3

A simple distributed data streaming pipeline built with Python, Kafka (Redpanda), and Flask, designed to process your Chrome browser history.

## Overview

* **Browser history**: Exported from Chrome in JSON format.
* **Download script**: `download_from_gdrive.py` fetches the history JSON from Google Drive and saves it to `data/history.json`.
* **Docker**: Containers mount `data/history.json` for processing.

## Prerequisites

* [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
* Python 3.9+

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/mykytavarenyk/data_streaming_3.git
   cd data_streaming_3
   ```

2. **Download browser history JSON**

   ```bash
   python download_from_gdrive.py <google_drive_link>
   ```

   Example:

   ```bash
   python3 download_from_gdrive.py https://drive.google.com/file/d/1DZxdtc-4l1y1-CdZgs8pdFmzSWs8DGhZ/view?usp=drive_link
   ```

   This will create a `data/` folder (if it doesn't exist) and save the file as `data/history.json`.

3. **Start services**

   ```bash
   docker compose up -d
   ```

## Streaming Data

Trigger the data generator to read `history.json` and publish messages to Kafka:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"json_path":"/app/history.json"}'
```

## Cleanup

```bash
docker compose down
```
