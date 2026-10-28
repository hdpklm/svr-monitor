import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

import os
os.environ.setdefault("BASE_URL", "http://localhost:8000")
os.environ.setdefault("GOOGLE_CLIENT_ID", "dummy")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "dummy")
os.environ.setdefault("SESSION_SECRET", "dummy_secret_dummy_secret_123456789")
os.environ.setdefault("DB_NAME", "monitor")
os.environ.setdefault("DB_USER", "monitor")
os.environ.setdefault("DB_PASSWORD", "secret")
os.environ.setdefault("ADMIN_EMAILS", "admin@example.com,owner@domain.com")

def test_imports():
	from web import settings
	assert "admin@example.com" in settings.ADMIN_EMAILS
	assert "owner@domain.com" in settings.ADMIN_EMAILS
	assert "user@example.com" not in settings.ADMIN_EMAILS
	print("settings test passed")

	from web import repo_users, deps, routes_auth, routes_pages, routes_admin
	print("all imports passed")

if __name__ == "__main__":
	test_imports()
	print("All unit tests passed successfully!")

