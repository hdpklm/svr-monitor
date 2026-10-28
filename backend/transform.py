def to_metric_rows(client_id, payload):
	return [
		(client_id, payload.timestamp, name, stat.avg, stat.min, stat.max)
		for name, stat in payload.metrics.items()
	]


def to_slow_rows(client_id, payload):
	rows = []
	for name, value in payload.slow.items():
		if isinstance(value, dict):
			rows.extend((client_id, payload.timestamp, f"{name}:{key}", item) for key, item in value.items())
		else:
			rows.append((client_id, payload.timestamp, name, value))
	return rows
