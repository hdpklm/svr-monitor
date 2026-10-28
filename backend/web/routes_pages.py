from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web import settings
from web.deps import current_user
from web.templating import templates

router = APIRouter()


@router.get("/")
async def home(user=Depends(current_user)):
	if not user:
		return RedirectResponse("/login", status_code=303)
	if not user.get("is_active"):
		return RedirectResponse("/pending", status_code=303)
	return RedirectResponse("/metrics", status_code=303)


@router.get("/pending", response_class=HTMLResponse)
async def pending_page(request: Request, user=Depends(current_user)):
	if not user:
		return RedirectResponse("/login", status_code=303)
	if user.get("is_active"):
		return RedirectResponse("/metrics", status_code=303)
	return templates.TemplateResponse(request, "pending.html", {"user": user})


@router.get("/thanks", response_class=HTMLResponse)
async def thanks_page(request: Request, user=Depends(current_user)):
	return templates.TemplateResponse(
		request,
		"thanks.html",
		{"user": user, "donate_url": settings.DONATE_URL},
	)
