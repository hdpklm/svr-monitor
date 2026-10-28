from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web import repo_users
from web.deps import admin_page_user
from web.templating import templates

router = APIRouter()


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, user=Depends(admin_page_user)):
	users_list = await repo_users.list_all()
	return templates.TemplateResponse(
		request,
		"admin_users.html",
		{"user": user, "users_list": users_list},
	)


@router.post("/admin/users/{user_id}/activate")
async def activate_user(user_id: int, user=Depends(admin_page_user)):
	await repo_users.set_active(user_id, True)
	return RedirectResponse("/admin/users", status_code=303)


@router.post("/admin/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, user=Depends(admin_page_user)):
	if user_id == user["id"]:
		raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
	await repo_users.set_active(user_id, False)
	return RedirectResponse("/admin/users", status_code=303)


@router.post("/admin/users/{user_id}/toggle-admin")
async def toggle_admin_user(user_id: int, user=Depends(admin_page_user)):
	if user_id == user["id"]:
		raise HTTPException(status_code=400, detail="No puedes modificar tus propios permisos de administrador")
	target = await repo_users.find(user_id)
	if not target:
		raise HTTPException(status_code=404, detail="Usuario no encontrado")
	new_admin_state = not target["is_admin"]
	await repo_users.set_admin(user_id, new_admin_state)
	return RedirectResponse("/admin/users", status_code=303)

