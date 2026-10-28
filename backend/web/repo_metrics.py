import database

AGGREGATE_SQL = """
SELECT
	(TIMESTAMPDIFF(SECOND, '1970-01-01 00:00:00', ts) DIV %s) * %s AS bucket,
	name,
	AVG(avg_value),
	MIN(min_value),
	MAX(max_value)
FROM metrics
WHERE client_id = %s AND ts >= %s
GROUP BY bucket, name
ORDER BY bucket
"""

LATEST_SLOW_SQL = """
SELECT s.name, s.value
FROM slow_metrics s
JOIN (
	SELECT name, MAX(ts) AS ts
	FROM slow_metrics
	WHERE client_id = %s
	GROUP BY name
) latest ON latest.name = s.name AND latest.ts = s.ts
WHERE s.client_id = %s
"""


async def aggregate(client_id, since, step):
	async with database.transaction() as cursor:
		await cursor.execute(AGGREGATE_SQL, (step, step, client_id, since))
		return await cursor.fetchall()


async def latest_slow(client_id):
	async with database.transaction() as cursor:
		await cursor.execute(LATEST_SLOW_SQL, (client_id, client_id))
		return {name: float(value) for name, value in await cursor.fetchall()}
