import asyncio
import sys

import database
import repository
import security


async def create(name):
	key = security.generate_key()
	await database.open_pool()
	try:
		client_id = await repository.insert_client(name, security.hash_key(key))
	finally:
		await database.close_pool()
	return client_id, key


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("uso: python create_client.py <nombre>")
	client_id, key = asyncio.run(create(sys.argv[1]))
	print(f"cliente: {client_id}")
	print(f"MONITOR_API_KEY={key}")
