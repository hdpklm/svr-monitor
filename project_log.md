

### 📝 Registro: [v1.1.0] - Implementación de roles de administrador y aprobación de nuevos usuarios
- **date-time**: 2026-10-29 00:18:00
- **Problema**:
	- Cualquier usuario autenticado por Google accedía directamente al sistema sin control previo. Se requería que los nuevos usuarios registrados queden inactivos por defecto, mostrando una pantalla en inglés ("Please wait for an administrator to accept your account"), sin acceso a ninguna métrica o dispositivo hasta que un administrador apruebe su cuenta.
- **Causa**:
	- No existían los campos `is_active` ni `is_admin` en la base de datos ni lógica de autorización en las dependencias y rutas web.
- **Solución**:
	- Se añadieron los campos `is_active` e `is_admin` al esquema de base de datos (`schema_web.sql`) y migración automática en el arranque (`repo_users.ensure_schema()`).
	- Se configuró la variable `ADMIN_EMAILS` en `settings.py`, `docker-compose.override.yml` y `.env.web.example` para otorgar automáticamente rol de administrador y activación a correos designados.
	- Se actualizaron las dependencias (`web/deps.py`) y enrutadores (`routes_auth.py`, `routes_pages.py`) para redirigir a los usuarios inactivos a `/pending`.
	- Se creó la plantilla `web/templates/pending.html` con el mensaje requerido en inglés y bloqueo total de navegación.
	- Se implementó la ruta y panel de administración (`web/routes_admin.py` y `web/templates/admin_users.html`) para listar usuarios, aprobarlos (`/activate`), desactivarlos (`/deactivate`) o alternar rol (`/toggle-admin`).
	- Se creó el script CLI `backend/set_admin.py` para activar o conceder rol de administrador directamente por consola.

### 📝 Registro: [v1.2.0] - Implementación del script de migración automática de base de datos
- **date-time**: 2026-10-29 00:24:00
- **Problema**:
	- La creación de tablas dependía de la inicialización de volúmenes de MySQL vía docker-entrypoint o de la inyección manual de scripts SQL por parte del usuario, impidiendo que las tablas se creen solas en bases de datos existentes o en entornos sin docker.
- **Causa**:
	- No existía un script dedicado de migración/sincronización equivalente a `scripts/db_migration.py` de `cuentas-claras`.
- **Solución**:
	- Se implementó `backend/scripts/db_migration.py` con la función `sync_db()`, encargada de crear automáticamente todas las tablas faltantes (`users`, `clients`, `metrics`, `slow_metrics`), sincronizar columnas nuevas (`is_active`, `is_admin`, `user_id`, `description`, `key_hint`) y asegurar claves foráneas e índices.
	- Se integró `sync_db()` en el `lifespan` de FastAPI en `main.py` para ejecutarse automáticamente al arrancar el servidor backend.
	- Se actualizaron los `Dockerfile` y `Dockerfile.web` para incluir el directorio `scripts/`.
	- Se añadió test unitario de verificación en `LLM_Test/gemini/database/test_migration.py`.