from fastapi.templating import Jinja2Templates

from web import settings

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def asset_url(path):
	file = settings.STATIC_DIR / path
	version = int(file.stat().st_mtime) if file.exists() else 0
	return f"/static/{path}?v={version}"


templates.env.globals["asset"] = asset_url
templates.env.globals["donate_url"] = settings.DONATE_URL
