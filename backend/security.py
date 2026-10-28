import hashlib
import secrets

KEY_PREFIX = "mk_"
KEY_BYTES = 48
MAX_KEY_LENGTH = 128


def generate_key():
	return KEY_PREFIX + secrets.token_urlsafe(KEY_BYTES)


def hash_key(key):
	return hashlib.sha256(key.encode()).hexdigest()
