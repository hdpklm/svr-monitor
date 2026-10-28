from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web.deps import current_user
from web.templating import templates

router = APIRouter()


@router.get("/")
async def home(user=Depends(current_user)):
	return RedirectResponse("/metrics" if user else "/login", status_code=303)


@router.get("/thanks", response_class=HTMLResponse)
async def thanks_page(request: Request, user=Depends(current_user)):
	return templates.TemplateResponse(request, "thanks.html", {"user": user})
