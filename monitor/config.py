import os
import socket

SERVER_URL = os.environ.get("MONITOR_URL", "https://tu-servidor/api/metrics")
API_KEY = os.environ.get("MONITOR_API_KEY", "")
HOST_ID = os.environ.get("MONITOR_HOST", socket.gethostname())

SAMPLE_HZ = 20
WINDOW_SECONDS = 60
DISK_PATHS = ["/"]

SEND_TIMEOUT = 10
MAX_PENDING = 120
