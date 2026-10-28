from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

MAX_NAME_LENGTH = 128
MAX_ENTRIES = 100


class Stat(BaseModel):
	avg: float
	min: float
	max: float


class Payload(BaseModel):
	timestamp: datetime
	window_seconds: int = Field(gt=0)
	samples: int = Field(ge=0)
	metrics: dict[str, Stat]
	slow: dict[str, float | dict[str, float]] = Field(default_factory=dict)

	@field_validator("timestamp")
	@classmethod
	def to_naive_utc(cls, value):
		if value.tzinfo is None:
			return value
		return value.astimezone(timezone.utc).replace(tzinfo=None)

	@field_validator("metrics", "slow")
	@classmethod
	def limit_names(cls, entries):
		if len(entries) > MAX_ENTRIES:
			raise ValueError("demasiadas entradas")
		for name, value in entries.items():
			longest = len(name)
			if isinstance(value, dict):
				longest += 1 + max((len(key) for key in value), default=0)
			if longest > MAX_NAME_LENGTH:
				raise ValueError("nombre demasiado largo")
		return entries
