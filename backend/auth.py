from fastapi import Header, HTTPException

import repository
import security


async def authenticate(x_api_key: str | None = Header(default=None)) -> int:
	if not x_api_key or len(x_api_key) > security.MAX_KEY_LENGTH:
		raise HTTPException(status_code=401, detail="unauthorized")
	client_id = await repository.find_client_id(security.hash_key(x_api_key))
	if client_id is None:
		raise HTTPException(status_code=401, detail="unauthorized")
	return client_id
