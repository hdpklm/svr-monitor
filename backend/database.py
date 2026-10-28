from contextlib import asynccontextmanager

import aiomysql

import config

_pool = None


async def open_pool():
	global _pool
	_pool = await aiomysql.create_pool(
		host=config.DB_HOST,
		port=config.DB_PORT,
		user=config.DB_USER,
		password=config.DB_PASSWORD,
		db=config.DB_NAME,
		minsize=1,
		maxsize=config.DB_POOL_SIZE,
		charset="utf8mb4",
		autocommit=False,
	)


async def close_pool():
	_pool.close()
	await _pool.wait_closed()


@asynccontextmanager
async def transaction():
	async with _pool.acquire() as connection:
		async with connection.cursor() as cursor:
			try:
				yield cursor
				await connection.commit()
			except Exception:
				await connection.rollback()
				raise
