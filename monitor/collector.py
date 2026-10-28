import os
import time

import psutil

import config

MB = 1024 * 1024


class FastCollector:
	def __init__(self):
		psutil.cpu_percent(interval=None)
		self._net = psutil.net_io_counters()
		self._disk = psutil.disk_io_counters()
		self._last = time.monotonic()

	def read(self):
		now = time.monotonic()
		dt = max(now - self._last, 1e-6)
		net = psutil.net_io_counters()
		disk = psutil.disk_io_counters()
		mem = psutil.virtual_memory()

		sample = {
			"cpu_percent": psutil.cpu_percent(interval=None),
			"ram_percent": mem.percent,
			"ram_used_mb": mem.used / MB,
			"net_rx_kbps": _rate(net.bytes_recv, self._net.bytes_recv, dt) * 8 / 1000,
			"net_tx_kbps": _rate(net.bytes_sent, self._net.bytes_sent, dt) * 8 / 1000,
		}
		if disk and self._disk:
			sample["disk_read_mbps"] = _rate(disk.read_bytes, self._disk.read_bytes, dt) / MB
			sample["disk_write_mbps"] = _rate(disk.write_bytes, self._disk.write_bytes, dt) / MB

		self._net, self._disk, self._last = net, disk, now
		return sample


def read_slow():
	data = {
		"load1": os.getloadavg()[0],
		"swap_percent": psutil.swap_memory().percent,
		"disk_used_percent": {path: psutil.disk_usage(path).percent for path in config.DISK_PATHS},
		"uptime_s": int(time.time() - psutil.boot_time()),
	}
	temperature = _max_temperature()
	if temperature is not None:
		data["cpu_temp_c"] = temperature
	return data


def _rate(current, previous, dt):
	return max(current - previous, 0) / dt


def _max_temperature():
	read = getattr(psutil, "sensors_temperatures", None)
	if read is None:
		return None
	values = [entry.current for entries in read().values() for entry in entries]
	return max(values) if values else None
