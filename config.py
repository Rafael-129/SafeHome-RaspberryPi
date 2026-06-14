import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_URL = os.getenv("CAMERA_URL")
CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL") or (
    CAMERA_URL.replace("/shot.jpg", "/video") if CAMERA_URL else None
)
API_BASE_URL = os.getenv("API_BASE_URL")
ENCODINGS_DIR = os.getenv("ENCODINGS_DIR", "data/encodings")
TOLERANCE = float(os.getenv("TOLERANCE", 0.5))
SCAN_INTERVAL = float(os.getenv("SCAN_INTERVAL", 2.5))
LOG_FILE = os.getenv("LOG_FILE", "logs/scanner.log")
PURGE_TOKEN = os.getenv("PURGE_TOKEN")

RESIDENTES = {
    "rafael": 4,
}