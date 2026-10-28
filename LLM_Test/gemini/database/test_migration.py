import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

os.environ.setdefault("DB_NAME", "monitor")
os.environ.setdefault("DB_USER", "monitor")
os.environ.setdefault("DB_PASSWORD", "secret")

def test_migration_definitions():
	from scripts import db_migration
	assert "users" in db_migration.TABLE_DEFINITIONS
	assert "clients" in db_migration.TABLE_DEFINITIONS
	assert "metrics" in db_migration.TABLE_DEFINITIONS
	assert "slow_metrics" in db_migration.TABLE_DEFINITIONS
	assert "is_active" in db_migration.COLUMN_DEFINITIONS["users"]
	assert "is_admin" in db_migration.COLUMN_DEFINITIONS["users"]
	assert "user_id" in db_migration.COLUMN_DEFINITIONS["clients"]
	print("Migration structure tests passed successfully!")

if __name__ == "__main__":
	test_migration_definitions()

