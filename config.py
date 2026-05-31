import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_URL = os.getenv("CAMERA_URL")
API_BASE_URL = os.getenv("API_BASE_URL")
ENCODINGS_DIR = os.getenv("ENCODINGS_DIR", "data/encodings")
TOLERANCE = float(os.getenv("TOLERANCE", 0.5))
SCAN_INTERVAL = float(os.getenv("SCAN_INTERVAL", 2.5))
LOG_FILE = os.getenv("LOG_FILE", "logs/scanner.log")

RESIDENTES = {
    "rafael": 4,
    "sandra": None
}