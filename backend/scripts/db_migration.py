import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
	sys.path.insert(0, str(backend_dir))

# Automatically load .env if environment variables are missing
def load_env_file():
	for path in (Path(".env"), backend_dir / ".env", backend_dir.parent / ".env"):
		if path.is_file():
			with open(path, "r", encoding="utf-8") as f:
				for line in f:
					line = line.strip()
					if line and not line.startswith("#") and "=" in line:
						key, val = line.split("=", 1)
						key = key.strip()
						val = val.strip().strip("'\"")
						os.environ.setdefault(key, val)
			break

load_env_file()

import database

TABLE_DEFINITIONS = {
	"users": """
		CREATE TABLE IF NOT EXISTS users (
			id INT UNSIGNED NOT NULL AUTO_INCREMENT,
			google_sub VARCHAR(255) NOT NULL,
			email VARCHAR(255) NOT NULL,
			name VARCHAR(255) NOT NULL,
			is_active BOOLEAN NOT NULL DEFAULT FALSE,
			is_admin BOOLEAN NOT NULL DEFAULT FALSE,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			PRIMARY KEY (id),
			UNIQUE KEY uq_users_google_sub (google_sub)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	""",
	"clients": """
		CREATE TABLE IF NOT EXISTS clients (
			id INT UNSIGNED NOT NULL AUTO_INCREMENT,
			name VARCHAR(100) NOT NULL,
			key_hash CHAR(64) NOT NULL,
			active TINYINT(1) NOT NULL DEFAULT 1,
			user_id INT UNSIGNED NULL,
			description VARCHAR(255) NULL,
			key_hint CHAR(4) NULL,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			last_seen DATETIME NULL,
			PRIMARY KEY (id),
			UNIQUE KEY uq_clients_key_hash (key_hash),
			KEY idx_clients_user (user_id)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	""",
	"metrics": """
		CREATE TABLE IF NOT EXISTS metrics (
			client_id INT UNSIGNED NOT NULL,
			name VARCHAR(128) NOT NULL,
			ts DATETIME NOT NULL,
			avg_value DOUBLE NOT NULL,
			min_value DOUBLE NOT NULL,
			max_value DOUBLE NOT NULL,
			PRIMARY KEY (client_id, name, ts),
			CONSTRAINT fk_metrics_client FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	""",
	"slow_metrics": """
		CREATE TABLE IF NOT EXISTS slow_metrics (
			client_id INT UNSIGNED NOT NULL,
			name VARCHAR(128) NOT NULL,
			ts DATETIME NOT NULL,
			value DOUBLE NOT NULL,
			PRIMARY KEY (client_id, name, ts),
			CONSTRAINT fk_slow_metrics_client FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	""",
}

COLUMN_DEFINITIONS = {
	"users": {
		"is_active": "BOOLEAN NOT NULL DEFAULT FALSE",
		"is_admin": "BOOLEAN NOT NULL DEFAULT FALSE",
	},
	"clients": {
		"user_id": "INT UNSIGNED NULL",
		"description": "VARCHAR(255) NULL",
		"key_hint": "CHAR(4) NULL",
	},
}


async def sync_db():
	print("Iniciando sincronización de base de datos...")

	# 1. Crear tablas si no existen
	async with database.transaction() as cursor:
		for table_name, create_sql in TABLE_DEFINITIONS.items():
			await cursor.execute(create_sql)
	print("Verificación de tablas completada (create_all).")

	# 2. Sincronizar columnas faltantes en tablas existentes
	async with database.transaction() as cursor:
		for table_name, columns in COLUMN_DEFINITIONS.items():
			await cursor.execute(
				"""
				SELECT COLUMN_NAME
				FROM information_schema.COLUMNS
				WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
				""",
				(table_name,),
			)
			existing = {row[0] for row in await cursor.fetchall()}

			for col_name, col_sql in columns.items():
				if col_name not in existing:
					print(f"Detectada columna faltante: {table_name}.{col_name}")
					alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {col_sql}"
					try:
						await cursor.execute(alter_sql)
						print(f"Éxito: Columna {col_name} añadida a {table_name}.")
					except Exception as e:
						print(f"Error al añadir {table_name}.{col_name}: {e}")

		# 3. Sincronizar foreign key fk_clients_user si aplica
		await cursor.execute(
			"""
			SELECT COUNT(*)
			FROM information_schema.TABLE_CONSTRAINTS
			WHERE CONSTRAINT_SCHEMA = DATABASE()
				AND TABLE_NAME = 'clients'
				AND CONSTRAINT_NAME = 'fk_clients_user'
			"""
		)
		fk_exists = (await cursor.fetchone())[0] > 0
		if not fk_exists:
			try:
				await cursor.execute(
					"""
					ALTER TABLE clients
					ADD CONSTRAINT fk_clients_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
					"""
				)
				print("Éxito: Restricción de clave foránea fk_clients_user añadida.")
			except Exception as e:
				# May fail if foreign key cannot be applied yet; non-critical
				pass

	print("Sincronización finalizada.")


async def main():
	await database.open_pool()
	try:
		await sync_db()
	finally:
		await database.close_pool()


if __name__ == "__main__":
	asyncio.run(main())

