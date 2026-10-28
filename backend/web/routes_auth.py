from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web import repo_users, settings
from web.deps import current_user
from web.oauth import oauth
from web.templating import templates

router = APIRouter()

CALLBACK_URL = f"{settings.BASE_URL}/auth/google/callback"
LOGIN_ERROR_URL = "/login?error=1"


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: int = 0, user=Depends(current_user)):
	if user:
		if not user.get("is_active"):
			return RedirectResponse("/pending", status_code=303)
		return RedirectResponse("/metrics", status_code=303)
	return templates.TemplateResponse(request, "login.html", {"user": None, "error": bool(error)})


@router.get("/auth/google")
async def start_google(request: Request):
	return await oauth.google.authorize_redirect(request, CALLBACK_URL)


@router.get("/auth/google/callback")
async def finish_google(request: Request):
	try:
		token = await oauth.google.authorize_access_token(request)
	except OAuthError:
		return RedirectResponse(LOGIN_ERROR_URL, status_code=303)

	info = token.get("userinfo") or {}
	if not (info.get("sub") and info.get("email") and info.get("email_verified")):
		return RedirectResponse(LOGIN_ERROR_URL, status_code=303)

	email = info["email"][:255]
	name = (info.get("name") or email)[:255]
	is_admin_candidate = email.lower() in settings.ADMIN_EMAILS
	user_id, is_active, _ = await repo_users.upsert_google(info["sub"], email, name, is_admin_email=is_admin_candidate)

	request.session.clear()
	request.session["user_id"] = user_id
	if not is_active:
		return RedirectResponse("/pending", status_code=303)
	return RedirectResponse("/metrics", status_code=303)


@router.post("/logout")
async def logout(request: Request):
	request.session.clear()
	return RedirectResponse("/login", status_code=303)
