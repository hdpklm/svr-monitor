import calendar
from datetime import datetime, timezone


def utc_now():
	return datetime.now(timezone.utc).replace(tzinfo=None)


def to_epoch(value):
	if value is None:
		return None
	return calendar.timegm(value.timetuple())


def from_epoch(seconds):
	return datetime.fromtimestamp(seconds, timezone.utc).replace(tzinfo=None)
