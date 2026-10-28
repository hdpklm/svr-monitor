# Monitor backend

Recibe las métricas del monitor, valida la clave del cliente y las guarda en MySQL.

## Archivos

| Archivo | Función |
|---|---|
| `main.py` | Rutas |
| `auth.py` | Valida la clave |
| `security.py` | Genera y hashea claves |
| `schemas.py` | Valida el JSON recibido |
| `transform.py` | Convierte el JSON en filas |
| `repository.py` | Consultas SQL |
| `database.py` | Pool de conexiones |
| `config.py` | Variables de entorno |
| `create_client.py` | Crea un cliente y su clave |
| `scripts/db_migration.py` | Sincronización automática de tablas y columnas en MySQL |
| `schema.sql` | Tablas |
| `Dockerfile` | Imagen del backend |

## Clave de cliente

- 384 bits aleatorios (`secrets.token_urlsafe(48)`), formato `mk_...`.
- En MySQL solo se guarda el hash SHA-256. La clave se muestra una vez al crearla.
- Cada clave pertenece a un cliente (`clients.id`). Las filas de métricas se guardan con ese `client_id`.
- Para revocarla: `UPDATE clients SET active = 0 WHERE id = X;`

## Instalación con Docker

`docker-compose.yml` y `.env.example` están en la raíz del proyecto, junto a las carpetas `backend` y `monitor`. Ejecuta todo desde la raíz.

**1. Variables**
```bash
cp .env.example .env
chmod 600 .env
```
Edita `.env` y cambia las dos contraseñas.

**2. Arrancar**
```bash
docker compose up -d --build
```

La primera vez MySQL crea la base de datos y ejecuta `schema.sql`. Si cambias `schema.sql` después, no se vuelve a ejecutar mientras exista el volumen `db_data`.

**3. Crear un cliente**
```bash
docker compose exec backend python create_client.py nombre-del-servidor
```

Copia `MONITOR_API_KEY=...` al monitor (`setup.sh` la pide).

**4. Comprobar**
```bash
docker compose ps
docker compose logs -f backend
```

El backend escucha solo en `127.0.0.1:8000`. Expónlo con nginx.

**Actualizar**
```bash
docker compose up -d --build
```

## Instalación sin Docker

**1. Base de datos**
```bash
mysql -u root -p -e "CREATE DATABASE monitor CHARACTER SET utf8mb4"
mysql -u root -p monitor < schema.sql
```

**2. Entorno**
```bash
uv venv venv
uv pip install -r requirements.txt --python venv/bin/python
```

**3. Variables**
```bash
cat > .env <<EOF
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=monitor
DB_PASSWORD=tu_password
DB_NAME=monitor
EOF
chmod 600 .env
```

**4. Crear un cliente**
```bash
set -a; . ./.env; set +a
venv/bin/python create_client.py nombre-del-servidor
```

**5. Arrancar**
```bash
venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

## HTTPS

Ponlo detrás de nginx con HTTPS. La clave viaja en la cabecera `X-API-Key` y sin HTTPS se puede interceptar.

```
location /api/metrics {
	proxy_pass http://127.0.0.1:8000;
	client_max_body_size 64k;
}
```

## Endpoint

`POST /api/metrics` con la cabecera `X-API-Key`.

| Respuesta | Significado |
|---|---|
| 204 | Guardado |
| 401 | Clave inválida o cliente desactivado |
| 422 | JSON inválido |

Si el monitor reenvía un dato repetido, se ignora (clave única `client_id + name + ts`).

## Tablas

- `clients`: clientes, hash de la clave y `last_seen`.
- `metrics`: `avg_value`, `min_value`, `max_value` por métrica y minuto.
- `slow_metrics`: valores únicos por minuto (`disk_used_percent:/`, `load1`...).

Consulta de ejemplo:
```sql
SELECT ts, avg_value, max_value
FROM metrics
WHERE client_id = 1 AND name = 'cpu_percent' AND ts >= NOW() - INTERVAL 1 HOUR
ORDER BY ts;
```
