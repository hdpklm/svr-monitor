from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from main import app
from web import settings
from web import routes_auth, routes_devices, routes_metrics, routes_pages

app.add_middleware(
	SessionMiddleware,
	secret_key=settings.SESSION_SECRET,
	max_age=settings.SESSION_MAX_AGE,
	same_site="lax",
	https_only=settings.HTTPS_ONLY,
)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

for module in (routes_auth, routes_pages, routes_metrics, routes_devices):
	app.include_router(module.router)
