import os
import re
import sys
import requests
import json

def extract_file_id(url_or_id: str) -> str:
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url_or_id)
    if m:
        return m.group(1)
    m = re.search(r'id=([a-zA-Z0-9_-]+)', url_or_id)
    if m:
        return m.group(1)
    return url_or_id.strip()

def download_from_drive(file_id: str) -> requests.Response:
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    resp = session.get(URL, params={"id": file_id}, stream=True)
    for k, v in resp.cookies.items():
        if k.startswith("download_warning"):
            resp = session.get(URL, params={"id": file_id, "confirm": v}, stream=True)
            break
    resp.raise_for_status()
    return resp

def save_response(resp: requests.Response, dest_path: str):
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=32_768):
            if chunk:
                f.write(chunk)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <gdrive_url_or_file_id>")
        sys.exit(1)

    url_or_id = sys.argv[1]
    file_id = extract_file_id(url_or_id)

    # Prepare data/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir   = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    dest_path = os.path.join(data_dir, "history.json")
    print(f"Downloading file {file_id} → {dest_path} …")

    resp = download_from_drive(file_id)
    save_response(resp, dest_path)
    print("✅ Download complete.")

    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            json.load(f)
        print("✅ Valid JSON.")
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: saved file is not valid JSON:\n  {e}")

if __name__ == "__main__":
    main()
