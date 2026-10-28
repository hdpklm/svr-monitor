import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

BASE_URL = os.environ["BASE_URL"].rstrip("/")
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
SESSION_SECRET = os.environ["SESSION_SECRET"]
DONATE_URL = os.environ.get("DONATE_URL", "")
MAX_DEVICES = int(os.environ.get("MAX_DEVICES", "10"))
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]

SESSION_MAX_AGE = 60 * 60 * 24 * 30
HTTPS_ONLY = BASE_URL.startswith("https://")
ONLINE_SECONDS = 180
