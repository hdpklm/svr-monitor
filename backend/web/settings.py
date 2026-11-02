import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "super_secret_debug_session_key_1234567890")
DONATE_URL = os.environ.get("DONATE_URL", "")
MAX_DEVICES = int(os.environ.get("MAX_DEVICES", "10"))
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]
DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

SESSION_MAX_AGE = 60 * 60 * 24 * 30
HTTPS_ONLY = BASE_URL.startswith("https://")
ONLINE_SECONDS = 180
