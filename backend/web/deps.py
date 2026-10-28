from fastapi import HTTPException, Request

from web import repo_users


async def current_user(request: Request):
	user_id = request.session.get("user_id")
	if user_id is None:
		return None
	return await repo_users.find(user_id)


async def page_user(request: Request):
	user = await current_user(request)
	if user is None:
		raise HTTPException(status_code=303, headers={"Location": "/login"})
	return user


async def api_user(request: Request):
	user = await current_user(request)
	if user is None:
		raise HTTPException(status_code=401, detail="No has iniciado sesión")
	return user
