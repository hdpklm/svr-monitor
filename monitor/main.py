import logging
import time
from datetime import datetime, timezone

import config
from aggregator import Aggregator
from collector import FastCollector, read_slow
from sender import Sender


def build_payload(metrics, samples, slow):
	return {
		"host": config.HOST_ID,
		"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
		"window_seconds": config.WINDOW_SECONDS,
		"samples": samples,
		"metrics": metrics,
		"slow": slow,
	}


def run():
	collector = FastCollector()
	aggregator = Aggregator()
	sender = Sender()

	period = 1 / config.SAMPLE_HZ
	next_tick = time.monotonic()
	window_end = next_tick + config.WINDOW_SECONDS

	while True:
		aggregator.add(collector.read())

		if time.monotonic() >= window_end:
			metrics, samples = aggregator.flush()
			sender.submit(build_payload(metrics, samples, read_slow()))
			window_end += config.WINDOW_SECONDS

		next_tick += period
		delay = next_tick - time.monotonic()
		if delay > 0:
			time.sleep(delay)
		else:
			next_tick = time.monotonic()


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
	run()
