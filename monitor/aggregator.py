class _Stat:
	__slots__ = ("count", "total", "low", "high")

	def __init__(self, value):
		self.count = 1
		self.total = value
		self.low = value
		self.high = value

	def add(self, value):
		self.count += 1
		self.total += value
		if value < self.low:
			self.low = value
		if value > self.high:
			self.high = value


class Aggregator:
	def __init__(self):
		self._stats = {}

	def add(self, sample):
		for name, value in sample.items():
			stat = self._stats.get(name)
			if stat is None:
				self._stats[name] = _Stat(value)
			else:
				stat.add(value)

	def flush(self):
		result = {
			name: {
				"avg": round(stat.total / stat.count, 2),
				"min": round(stat.low, 2),
				"max": round(stat.high, 2),
			}
			for name, stat in self._stats.items()
		}
		samples = max((stat.count for stat in self._stats.values()), default=0)
		self._stats = {}
		return result, samples
