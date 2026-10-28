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
	if not user.get("is_active"):
		raise HTTPException(status_code=303, headers={"Location": "/pending"})
	return user


async def admin_page_user(request: Request):
	user = await page_user(request)
	if not user.get("is_admin"):
		raise HTTPException(status_code=403, detail="Acceso denegado: permisos de administrador requeridos")
	return user


async def api_user(request: Request):
	user = await current_user(request)
	if user is None:
		raise HTTPException(status_code=401, detail="No has iniciado sesión")
	if not user.get("is_active"):
		raise HTTPException(status_code=403, detail="Cuenta inactiva. Espera a que un administrador te dé acceso.")
	return user


async def admin_api_user(request: Request):
	user = await api_user(request)
	if not user.get("is_admin"):
		raise HTTPException(status_code=403, detail="Acceso denegado: permisos de administrador requeridos")
	return user
