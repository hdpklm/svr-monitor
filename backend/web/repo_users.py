import database
from web.rows import as_dicts


async def find(user_id):
	async with database.transaction() as cursor:
		await cursor.execute(
			"SELECT id, email, name, is_active, is_admin, created_at, last_login FROM users WHERE id = %s",
			(user_id,),
		)
		rows = as_dicts(cursor, await cursor.fetchall())
	if not rows:
		return None
	user = rows[0]
	user["is_active"] = bool(user["is_active"])
	user["is_admin"] = bool(user["is_admin"])
	return user


async def upsert_google(sub, email, name, is_admin_email=False):
	async with database.transaction() as cursor:
		await cursor.execute("SELECT id, is_active, is_admin FROM users WHERE google_sub = %s", (sub,))
		row = await cursor.fetchone()
		if row:
			user_id, is_active, is_admin = row[0], bool(row[1]), bool(row[2])
			if is_admin_email and (not is_admin or not is_active):
				is_admin = True
				is_active = True
				await cursor.execute(
					"UPDATE users SET email = %s, name = %s, is_active = %s, is_admin = %s, last_login = CURRENT_TIMESTAMP WHERE id = %s",
					(email, name, is_active, is_admin, user_id),
				)
			else:
				await cursor.execute(
					"UPDATE users SET email = %s, name = %s, last_login = CURRENT_TIMESTAMP WHERE id = %s",
					(email, name, user_id),
				)
			return user_id, is_active, is_admin

		is_active = True if is_admin_email else False
		is_admin = True if is_admin_email else False
		await cursor.execute(
			"INSERT INTO users (google_sub, email, name, is_active, is_admin) VALUES (%s, %s, %s, %s, %s)",
			(sub, email, name, is_active, is_admin),
		)
		return cursor.lastrowid, is_active, is_admin


async def list_all():
	async with database.transaction() as cursor:
		await cursor.execute(
			"SELECT id, email, name, is_active, is_admin, created_at, last_login FROM users ORDER BY id DESC"
		)
		rows = as_dicts(cursor, await cursor.fetchall())
	for row in rows:
		row["is_active"] = bool(row["is_active"])
		row["is_admin"] = bool(row["is_admin"])
	return rows


async def set_active(user_id, active: bool):
	async with database.transaction() as cursor:
		await cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", (active, user_id))


async def set_admin(user_id, admin: bool):
	async with database.transaction() as cursor:
		await cursor.execute("UPDATE users SET is_admin = %s WHERE id = %s", (admin, user_id))
