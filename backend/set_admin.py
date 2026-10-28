import asyncio
import sys

import database


async def grant_admin(identifier):
	await database.open_pool()
	try:
		async with database.transaction() as cursor:
			if identifier.isdigit():
				await cursor.execute("SELECT id, email, name FROM users WHERE id = %s", (int(identifier),))
			else:
				await cursor.execute("SELECT id, email, name FROM users WHERE email = %s", (identifier,))
			row = await cursor.fetchone()
			if not row:
				sys.exit(f"Usuario no encontrado: {identifier}")
			user_id, email, name = row[0], row[1], row[2]
			await cursor.execute("UPDATE users SET is_active = 1, is_admin = 1 WHERE id = %s", (user_id,))
			print(f"Usuario {name} ({email}, id={user_id}) ahora es Administrador y está Activo.")
	finally:
		await database.close_pool()


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("uso: python set_admin.py <id_o_email>")
	asyncio.run(grant_admin(sys.argv[1]))

