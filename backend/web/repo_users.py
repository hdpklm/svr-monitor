import database
from web.rows import as_dicts


async def find(user_id):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id, email, name FROM users WHERE id = %s", (user_id,))
		rows = as_dicts(cursor, await cursor.fetchall())
	return rows[0] if rows else None


async def upsert_google(sub, email, name):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id FROM users WHERE google_sub = %s", (sub,))
		row = await cursor.fetchone()
		if row:
			await cursor.execute(
				"UPDATE users SET email = %s, name = %s, last_login = CURRENT_TIMESTAMP WHERE id = %s",
				(email, name, row[0]),
			)
			return row[0]
		await cursor.execute(
			"INSERT INTO users (google_sub, email, name) VALUES (%s, %s, %s)",
			(sub, email, name),
		)
		return cursor.lastrowid
