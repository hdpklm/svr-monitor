import logging
import queue
import threading
from collections import deque

import requests

import config

log = logging.getLogger("monitor.sender")

RETRYABLE_STATUS = {408, 429}


class Sender:
	def __init__(self):
		self._session = requests.Session()
		self._session.headers.update({"X-API-Key": config.API_KEY})
		self._queue = queue.Queue()
		self._pending = deque(maxlen=config.MAX_PENDING)
		threading.Thread(target=self._worker, daemon=True).start()

	def submit(self, payload):
		self._queue.put(payload)

	def _worker(self):
		while True:
			self._pending.append(self._queue.get())
			self._deliver_pending()

	def _deliver_pending(self):
		while self._pending:
			if not self._post(self._pending[0]):
				return
			self._pending.popleft()

	def _post(self, payload):
		try:
			response = self._session.post(config.SERVER_URL, json=payload, timeout=config.SEND_TIMEOUT)
		except requests.RequestException as error:
			log.warning("envio fallido: %s", error)
			return False
		retryable = response.status_code >= 500 or response.status_code in RETRYABLE_STATUS
		if response.status_code >= 400:
			log.warning("servidor respondio %s", response.status_code)
		return not retryable
