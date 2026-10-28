from typing import Literal

RangeKey = Literal["1h", "6h", "24h", "7d", "30d"]
StepKey = Literal["1m", "5m", "15m", "1h", "6h"]

RANGES = {"1h": 3600, "6h": 21600, "24h": 86400, "7d": 604800, "30d": 2592000}
STEPS = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "6h": 21600}

RANGE_LABELS = {
	"1h": "Última hora",
	"6h": "Últimas 6 horas",
	"24h": "Últimas 24 horas",
	"7d": "Últimos 7 días",
	"30d": "Últimos 30 días",
}
STEP_LABELS = {
	"1m": "1 minuto",
	"5m": "5 minutos",
	"15m": "15 minutos",
	"1h": "1 hora",
	"6h": "6 horas",
}

MAX_POINTS = 1500
STATS = ("avg", "min", "max")


def effective_step(range_seconds, step_seconds):
	minimum = -(-range_seconds // MAX_POINTS)
	wanted = max(step_seconds, minimum)
	for allowed in sorted(STEPS.values()):
		if allowed >= wanted:
			return allowed
	return max(STEPS.values())


def bucket_range(now_epoch, range_seconds, step):
	first = (now_epoch - range_seconds) // step * step
	last = now_epoch // step * step
	return list(range(first, last + step, step))


def build_series(rows, buckets):
	position = {bucket: index for index, bucket in enumerate(buckets)}
	size = len(buckets)
	result = {}
	for bucket, name, avg, low, high in rows:
		index = position.get(int(bucket))
		if index is None:
			continue
		entry = result.setdefault(name, {stat: [None] * size for stat in STATS})
		entry["avg"][index] = round(float(avg), 3)
		entry["min"][index] = round(float(low), 3)
		entry["max"][index] = round(float(high), 3)
	return result
