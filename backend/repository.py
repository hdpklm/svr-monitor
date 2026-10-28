import database

INSERT_METRICS = (
	"INSERT IGNORE INTO metrics (client_id, ts, name, avg_value, min_value, max_value) "
	"VALUES (%s, %s, %s, %s, %s, %s)"
)
INSERT_SLOW = "INSERT IGNORE INTO slow_metrics (client_id, ts, name, value) VALUES (%s, %s, %s, %s)"


async def find_client_id(key_hash):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id FROM clients WHERE key_hash = %s AND active = 1", (key_hash,))
		row = await cursor.fetchone()
	return row[0] if row else None


async def insert_client(name, key_hash):
	async with database.transaction() as cursor:
		await cursor.execute("INSERT INTO clients (name, key_hash) VALUES (%s, %s)", (name, key_hash))
		return cursor.lastrowid


async def save_payload(client_id, timestamp, metric_rows, slow_rows):
	async with database.transaction() as cursor:
		if metric_rows:
			await cursor.executemany(INSERT_METRICS, metric_rows)
		if slow_rows:
			await cursor.executemany(INSERT_SLOW, slow_rows)
		await cursor.execute("UPDATE clients SET last_seen = %s WHERE id = %s", (timestamp, client_id))
