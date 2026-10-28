import database
from web import settings, timeutil
from web.rows import as_dicts

LIST_SQL = """
SELECT
	c.id, c.name, c.description, c.key_hint, c.created_at, c.last_seen,
	(SELECT m.avg_value FROM metrics m
		WHERE m.client_id = c.id AND m.name = 'cpu_percent' AND m.ts = c.last_seen) AS cpu,
	(SELECT m.avg_value FROM metrics m
		WHERE m.client_id = c.id AND m.name = 'ram_percent' AND m.ts = c.last_seen) AS ram,
	(SELECT MAX(s.value) FROM slow_metrics s
		WHERE s.client_id = c.id AND s.ts = c.last_seen AND s.name LIKE 'disk_used_percent:%%') AS disk
FROM clients c
WHERE c.user_id = %s
ORDER BY c.name
"""


class DeviceLimitError(Exception):
	pass


def _present(row, now_epoch):
	last_seen = timeutil.to_epoch(row["last_seen"])
	row["last_seen"] = last_seen
	row["online"] = last_seen is not None and now_epoch - last_seen <= settings.ONLINE_SECONDS
	return row


async def list_for_user(user_id):
	async with database.transaction() as cursor:
		await cursor.execute(LIST_SQL, (user_id,))
		rows = as_dicts(cursor, await cursor.fetchall())
	now_epoch = timeutil.to_epoch(timeutil.utc_now())
	return [_present(row, now_epoch) for row in rows]


async def list_basic(user_id):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id, name FROM clients WHERE user_id = %s ORDER BY name", (user_id,))
		return as_dicts(cursor, await cursor.fetchall())


async def find_owned(user_id, device_id):
	async with database.transaction() as cursor:
		await cursor.execute(
			"SELECT id, name, last_seen FROM clients WHERE id = %s AND user_id = %s",
			(device_id, user_id),
		)
		rows = as_dicts(cursor, await cursor.fetchall())
	return rows[0] if rows else None


async def create(user_id, name, description, key_hash, key_hint):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT COUNT(*) FROM clients WHERE user_id = %s", (user_id,))
		(count,) = await cursor.fetchone()
		if count >= settings.MAX_DEVICES:
			raise DeviceLimitError
		await cursor.execute(
			"INSERT INTO clients (name, description, key_hash, key_hint, user_id) VALUES (%s, %s, %s, %s, %s)",
			(name, description or None, key_hash, key_hint, user_id),
		)
		return cursor.lastrowid


async def update(user_id, device_id, name, description):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id FROM clients WHERE id = %s AND user_id = %s", (device_id, user_id))
		if await cursor.fetchone() is None:
			return False
		await cursor.execute(
			"UPDATE clients SET name = %s, description = %s WHERE id = %s",
			(name, description or None, device_id),
		)
		return True


async def delete(user_id, device_id):
	async with database.transaction() as cursor:
		await cursor.execute("DELETE FROM clients WHERE id = %s AND user_id = %s", (device_id, user_id))
		return cursor.rowcount > 0
