# Project Status - Server Monitor v1.2.0

## Arquitectura: Arquitectura Hexagonal / HexArch
Sistema de monitorización ligera de métricas de servidores y panel web de visualización multiusuario.

## Mapeo de Modulos y Responsabilidades
### `backend`
- `main::receive_metrics`: Ingesta de métricas transmitidas por agentes mediante autenticación por clave de cliente.
- `app`: Configuración del servidor web FastAPI, sesiones y registro de enrutadores.
- `database`: Inicialización y gestión del pool asíncrono de conexiones a MySQL.
- `repository`: Consultas e inserciones en base de datos para métricas y clientes.
- `auth`: Autenticación de clientes mediante API keys.
- `set_admin`: Script CLI para conceder permisos de administrador y activación a usuarios.

### `backend/scripts`
- `db_migration::sync_db`: Sincronización automática de esquema MySQL (creación de tablas y columnas faltantes).

### `backend/web`
- `routes_auth`: Control de flujo de inicio de sesión con Google OAuth y cierre de sesión.
- `routes_pages`: Vistas HTML principales del panel y pantalla de espera para usuarios pendientes.
- `routes_devices`: Administración de dispositivos asociados al usuario autenticado.
- `routes_metrics`: Consulta y visualización de series temporales de métricas.
- `routes_admin`: Panel de control para administradores para aceptar o revocar acceso a usuarios.
- `repo_users`: Persistencia y gestión del ciclo de vida de usuarios, roles y estados.
- `repo_devices`: Acceso a datos de dispositivos vinculados a usuarios.
- `repo_metrics`: Agregaciones y series históricas de métricas por dispositivo.
- `deps`: Dependencias FastAPI para resolución y autorización de usuarios normales, activos y administradores.

## Endpoints / Interfaces Externas
- `[POST] /api/metrics` [Auth: ApiKey]:
	- **Params / Payload**: `{ timestamp: int, cpu: float, memory: {...}, disks: [...], networks: [...] }`
	- **Response**: `204 No Content`
	- **Descripcion**: Recepción de métricas de agentes.
- `[GET] /login` [Auth: Public]:
	- **Descripcion**: Página de inicio de sesión con Google.
- `[GET] /auth/google` [Auth: Public]:
	- **Descripcion**: Redirección hacia el proveedor OAuth de Google.
- `[GET] /auth/google/callback` [Auth: Public]:
	- **Descripcion**: Recepción del callback de Google y alta/inicio de sesión de usuario.
- `[POST] /logout` [Auth: Public]:
	- **Descripcion**: Cierre de sesión y limpieza de cookies.
- `[GET] /pending` [Auth: Session]:
	- **Descripcion**: Pantalla de espera para usuarios recién registrados en estado inactivo.
- `[GET] /metrics` [Auth: Session (Active User)]:
	- **Descripcion**: Panel interactivo de métricas del servidor seleccionado.
- `[GET] /devices` [Auth: Session (Active User)]:
	- **Descripcion**: Listado y alta de servidores monitorizados.
- `[GET] /admin/users` [Auth: Session (Admin)]:
	- **Descripcion**: Listado de usuarios para gestión de aprobaciones y roles.
- `[POST] /admin/users/{user_id}/activate` [Auth: Session (Admin)]:
	- **Descripcion**: Aprueba y activa el acceso de un usuario.
- `[POST] /admin/users/{user_id}/deactivate` [Auth: Session (Admin)]:
	- **Descripcion**: Revoca el acceso de un usuario.
- `[POST] /admin/users/{user_id}/toggle-admin` [Auth: Session (Admin)]:
	- **Descripcion**: Concede o retira privilegios de administrador a un usuario.

