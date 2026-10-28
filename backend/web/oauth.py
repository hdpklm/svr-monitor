from authlib.integrations.starlette_client import OAuth

from web import settings

GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth = OAuth()
oauth.register(
	name="google",
	client_id=settings.GOOGLE_CLIENT_ID,
	client_secret=settings.GOOGLE_CLIENT_SECRET,
	server_metadata_url=GOOGLE_METADATA_URL,
	client_kwargs={"scope": "openid email profile"},
)
