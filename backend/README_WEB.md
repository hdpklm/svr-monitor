# Interfaz web

Páginas servidas por FastAPI con Jinja2. Sin React ni CDN: Chart.js va incluido en `web/static/vendor`.

## Páginas

| Ruta | Contenido |
|---|---|
| `/login` | Entrar con Google |
| `/metrics` | Dispositivo, periodo, muestra cada (1 min a 6 h) y gráficas |
| `/devices` | Lista, añadir, editar y eliminar dispositivos |
| `/thanks` | Agradecimiento y botón de donación |

## Archivos nuevos

| Archivo | Función |
|---|---|
| `app.py` | Arranque: añade sesión, estáticos y rutas a `main.app` |
| `schema_web.sql` | Tabla `users` y columnas nuevas en `clients` |
| `Dockerfile.web` | Imagen con la web (usa `requirements-web.txt`) |
| `web/settings.py` | Variables de entorno |
| `web/routes_*.py` | Rutas: auth, páginas, métricas, dispositivos |
| `web/repo_*.py` | Consultas SQL |
| `web/series.py` | Periodos, agrupación y huecos sin datos |
| `web/templates/` | Páginas HTML |
| `web/static/` | CSS y JavaScript por módulos |

Los archivos anteriores no se han modificado.

## Login con Google

1. Entra en Google Cloud Console, **APIs y servicios**, **Credenciales**.
2. Crea un **ID de cliente de OAuth** de tipo **Aplicación web**.
3. En **URI de redireccionamiento autorizados** añade `https://TU_DOMINIO/auth/google/callback`.
4. Copia el ID y el secreto al `.env`.

## Variables nuevas

Añade al `.env` de la raíz (hay una plantilla en `.env.web.example`):

| Variable | Descripción |
|---|---|
| `BASE_URL` | URL pública, sin barra final |
| `GOOGLE_CLIENT_ID` | ID de cliente |
| `GOOGLE_CLIENT_SECRET` | Secreto de cliente |
| `SESSION_SECRET` | Clave larga y aleatoria |
| `DONATE_URL` | Enlace de donación (PayPal, Ko-fi, Stripe...) |
| `MAX_DEVICES` | Dispositivos por usuario (10 por defecto) |

Generar `SESSION_SECRET`:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Arrancar con Docker

`docker-compose.override.yml` se aplica solo junto a `docker-compose.yml`:

```bash
docker compose up -d --build
```

En una base de datos nueva, MySQL crea las tablas nuevas solo. Si ya tenías la base de datos creada, aplica el SQL una vez:

```bash
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' < backend/schema_web.sql
```

## Arrancar sin Docker

```bash
uv pip install -r requirements.txt -r requirements-web.txt --python venv/bin/python
mysql -u root -p monitor < schema_web.sql
set -a; . ./.env; set +a
venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

## nginx

Ahora la web y la API cuelgan del mismo dominio, así que redirige todo:

```
location / {
	proxy_pass http://127.0.0.1:8000;
	proxy_set_header Host $host;
	proxy_set_header X-Forwarded-Proto $scheme;
	client_max_body_size 64k;
}
```

## Cómo funcionan las muestras

El monitor envía un dato por minuto. En `/metrics`, **Muestra cada** agrupa esos datos en bloques (media de medias, mínimo de mínimos, máximo de máximos). Para que la página no cargue miles de puntos, el máximo es 1500 por gráfica. Si el periodo es muy largo, la muestra se amplía sola y la página lo indica.

Los huecos sin datos (servidor apagado) se ven como cortes en la línea.

## Dispositivos creados con `create_client.py`

Esos dispositivos no tienen usuario y no aparecen en la web. Para asignarlos:

```sql
UPDATE clients SET user_id = 1 WHERE id = 3;
```
