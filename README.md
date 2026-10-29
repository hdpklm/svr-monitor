# SVR-Monitor

Sistema de monitorización ligera de servidores en tiempo real con panel web, autenticación Google OAuth y almacenamiento de métricas en MySQL.

---

## 📑 Índice
1. [Modalidades: Con Google Auth vs Sin Google Auth](#-modalidades-con-google-auth-vs-sin-google-auth)
   - [Modo 1: Con autenticación de Google (Panel web multiusuario)](#modo-1-con-autenticación-de-google-panel-web-multiusuario)
   - [Modo 2: Sin autenticación de Google (Modo privado / Solo API)](#modo-2-sin-autenticación-de-google-modo-privado--solo-api)
2. [Servidor Central: Backend (Recoge los datos)](#1-servidor-central-backend-recoge-los-datos)
   - [Opción A: Despliegue con MySQL existente en el VPS (Sin DB)](#opción-a-despliegue-con-mysql-existente-en-el-vps-sin-db)
   - [Opción B: Despliegue todo en uno (Con MySQL incluido)](#opción-b-despliegue-todo-en-uno-con-mysql-incluido)
   - [Gestión de Administradores y Aprobación de Usuarios](#gestión-de-administradores-y-aprobación-de-usuarios)
   - [Proxy inverso (Nginx / HTTPS)](#proxy-inverso-nginx--https)
3. [Agente Monitor: En cada VPS (Envía los datos)](#2-agente-monitor-en-cada-vps-envía-los-datos)
   - [Obtener la clave de cliente](#paso-1-obtener-la-clave-del-dispositivo-api-key)
   - [Instalación del servicio en el VPS](#paso-2-instalar-el-servicio-en-el-vps-cliente)
   - [Comandos de gestión y logs](#paso-3-gestión-del-servicio-systemd)

---

## 🔐 Modalidades: Con Google Auth vs Sin Google Auth

El backend puede funcionar en dos modalidades según tus necesidades:

### Modo 1: Con autenticación de Google (Panel web multiusuario)

Permite entrar al panel web mediante Google OAuth para consultar gráficas interactivas, añadir dispositivos y gestionar permisos.

- **Imagen Docker usada:** `Dockerfile.web` (ejecuta `app:app`).
- **Variables requeridas en `.env`:**
  - `BASE_URL`: URL pública (ej. `https://monitor.tudominio.com`).
  - `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`: Credenciales OAuth de Google.
  - `SESSION_SECRET`: Clave aleatoria para firmar cookies de sesión.
  - `ADMIN_EMAILS`: Lista separada por comas de correos que serán administradores.
- **Cómo obtener las credenciales en Google Cloud Console:**
  1. Entra en [Google Cloud Console](https://console.cloud.google.com/) y crea o selecciona un proyecto.
  2. Ve a **APIs y servicios** > **Pantalla de consentimiento de OAuth**:
     - Tipo: **Externo**.
     - Rellena el nombre de la app y tu correo de soporte.
  3. Ve a **Credenciales** > **Crear credenciales** > **ID de cliente de OAuth**:
     - Tipo de aplicación: **Aplicación web**.
     - Nombre: `Monitor SVR` (o el que desees).
     - **URI de redireccionamiento autorizados:**
       `https://monitor.tudominio.com/auth/google/callback`
  4. Copia el **ID de cliente** y el **Secreto de cliente** a tu `.env`.

---

### Modo 2: Sin autenticación de Google (Modo privado / Solo API)

Ideal si solo quieres recolectar métricas en tu base de datos MySQL sin panel web público ni cuentas de usuario. No requiere configurar nada en Google Cloud ni claves de sesión.

- **Imagen Docker usada:** `Dockerfile` estándar (ejecuta `main:app`).
- **Variables requeridas en `.env`:** Únicamente las de MySQL (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).
- **Cómo activarlo:**
  - Si usas `docker-compose.no-db.yml`: añade `DOCKERFILE=Dockerfile` en tu `.env`.
  - Si usas `docker-compose.yml`: arráncalo sin `docker-compose.override.yml` (por defecto usa `Dockerfile`).
- **Cómo dar de alta dispositivos sin panel web:**
  Como no hay interfaz gráfica, generas las claves de los servidores directamente por terminal:
  ```bash
  docker exec -it vps-monitor python create_client.py "nombre-del-servidor"
  ```
  Esto devolverá el identificador del cliente y la clave `MONITOR_API_KEY=mk_...`.

---

# 1. Servidor Central: Backend (Recoge los datos)

---

### Opción A: Despliegue con MySQL existente en el VPS (Sin DB)

Usa esta opción si ya tienes un contenedor de MySQL corriendo en tu VPS (por ejemplo, llamado **`mysql-monitor`**) y solo quieres arrancar el backend (**`vps-monitor`**).

#### 1. Configurar `.env`
Copia la plantilla adecuada a `.env` en la raíz del proyecto:

- Para **Modo CON Google Auth**: `cp .env.web.example .env`
- Para **Modo SIN Google Auth**: `cp .env.example .env`

**Ejemplo `.env` (Con Google Auth):**
```ini
# Base de datos externa (tu contenedor existente)
DB_HOST=mysql-monitor
DB_PORT=3306
DB_NAME=monitor
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql

# Panel web y OAuth (opcional: deja DOCKERFILE vacío para Dockerfile.web)
DOCKERFILE=Dockerfile.web
BASE_URL=https://monitor.tudominio.com
GOOGLE_CLIENT_ID=tu_client_id_de_google
GOOGLE_CLIENT_SECRET=tu_client_secret_de_google
SESSION_SECRET=genera_una_clave_aleatoria_larga
ADMIN_EMAILS=tu-email@gmail.com
MAX_DEVICES=10
```

**Ejemplo `.env` (Sin Google Auth - Modo Privado):**
```ini
DB_HOST=mysql-monitor
DB_PORT=3306
DB_NAME=monitor
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DOCKERFILE=Dockerfile
```

> **Generar `SESSION_SECRET`:**
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(48))"
> ```

#### 2. Arrancar el contenedor `vps-monitor`
Ejecuta Docker Compose usando el archivo sin base de datos:

```bash
docker compose -f docker-compose.no-db.yml up -d --build
```

Esto compilará y arrancará el contenedor con el nombre **`vps-monitor`** en el puerto local `127.0.0.1:8000`.

#### 3. Conectar la red Docker entre `vps-monitor` y `mysql-monitor`
Para que el backend resuelva por nombre al contenedor de MySQL, ambos deben compartir una red de Docker:

```bash
# 1. Averigua el nombre de la red de tu contenedor mysql-monitor:
docker inspect mysql-monitor --format '{{range $net, $v := .NetworkSettings.Networks}}{{$net}}{{end}}'

# 2. Conecta vps-monitor a esa misma red:
docker network connect <nombre_de_la_red> vps-monitor
```

#### 4. Migración automática de tablas
Al arrancar, `vps-monitor` ejecutará automáticamente el script `scripts/db_migration.py` en la base de datos `mysql-monitor`, creando sin intervención manual todas las tablas (`users`, `clients`, `metrics`, `slow_metrics`) y columnas faltantes.

---

### Opción B: Despliegue todo en uno (Con MySQL incluido)

Si no tienes MySQL y prefieres que Docker Compose levante tanto la base de datos como el backend desde cero:

- **Con Google Auth:**
  ```bash
  cp .env.web.example .env
  # Configura MYSQL_ROOT_PASSWORD, DB_PASSWORD y credenciales de Google
  docker compose up -d --build
  ```
- **Sin Google Auth:**
  Renombra o elimina temporalmente `docker-compose.override.yml`:
  ```bash
  cp .env.example .env
  docker compose up -d --build
  ```

---

### Gestión de Administradores y Aprobación de Usuarios (Modo Web)

- **Nuevos usuarios:** Cualquier usuario que inicie sesión con Google queda en estado inactivo por defecto, viendo la pantalla en inglés:
  > *"Please wait for an administrator to accept your account"*
- **Primer administrador:** Los correos indicados en `ADMIN_EMAILS` se activan y ascienden a administrador automáticamente al iniciar sesión.
- **Asignar administrador por terminal:**
  ```bash
  docker exec -it vps-monitor python set_admin.py tu_correo@gmail.com
  ```
- **Panel de administración:** Desde la web en `/admin/users` puedes ver los usuarios pendientes y pulsar **Aceptar** para darles acceso inmediato.

---

### Proxy inverso (Nginx / HTTPS)

El backend escucha en `127.0.0.1:8000`. Configura un bloque en Nginx con certificado SSL (Let's Encrypt / Certbot):

```nginx
server {
    server_name monitor.tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 64k;
    }

    listen 443 ssl;
    # Rutas a certificados SSL...
}
```

---

# 2. Agente Monitor: En cada VPS (Envía los datos)

El agente es un proceso ligero en Python que recopila métricas 20 veces por segundo y envía un resumen agrupado (media, mínimo y máximo de CPU, RAM, disco y red) cada 60 segundos a la API del servidor central.

---

### Paso 1: Obtener la clave del dispositivo (API Key)

Tienes dos formas de obtener la clave `mk_...`:

1. **Desde la Web (si usas Modo Google Auth):**
   - Entra en tu panel web (`https://monitor.tudominio.com`).
   - Ve a **Dispositivos** (`/devices`) y pulsa **Añadir dispositivo**.
   - Asigna un nombre (ej. `vps-produccion`) y copia la clave generada.

2. **Por consola en el Servidor Central (válido para ambos modos):**
   ```bash
   docker exec -it vps-monitor python create_client.py "vps-produccion"
   ```

---

### Paso 2: Instalar el servicio en el VPS cliente

En cada servidor o VPS que quieras monitorizar:

1. **Copia la carpeta `monitor/` a ese servidor** (vía SCP, rsync o clonando el repo):
   ```bash
   # Ejemplo usando scp desde tu máquina:
   scp -r monitor/ usuario@ip-del-vps:~/monitor
   ```

2. **Entra en el servidor y ejecuta el instalador `setup.sh` con `sudo`:**

   **Modo con parámetros directos:**
   ```bash
   cd ~/monitor
   sudo bash setup.sh https://monitor.tudominio.com/api/metrics <TU_API_KEY_MK> "Nombre-Servidor"
   ```

   **Modo interactivo (te pedirá la URL y la clave):**
   ```bash
   cd ~/monitor
   sudo bash setup.sh
   ```

#### ¿Qué hace el instalador automáticamente?
- Instala el gestor rápido de Python `uv` si no está en el sistema.
- Crea un usuario de sistema seguro llamado `monitor` (sin acceso a shell).
- Copia los archivos del agente a `/srv/monitor`.
- Crea un entorno virtual y sus dependencias aisladas.
- Guarda la configuración en `/srv/monitor/.env` (permisos `600`).
- Registra, habilita y arranca el servicio systemd `/etc/systemd/system/monitor.service`.

---

### Paso 3: Gestión del servicio systemd

El monitor queda corriendo de forma continua como un servicio de fondo que reinicia solo ante fallos o reinicios del VPS:

```bash
# Ver el estado en tiempo real:
sudo systemctl status monitor

# Ver las transmisiones de métricas en vivo:
journalctl -u monitor -f

# Reiniciar el servicio:
sudo systemctl restart monitor

# Detener el servicio:
sudo systemctl stop monitor
```

---

### Paso 4: Comprobación final

- **En Modo Web:** Ve a tu panel web (`https://monitor.tudominio.com/metrics`). En menos de 1 minuto el servidor aparecerá con estado **En línea** y podrás ver las curvas de CPU, memoria, I/O de disco y tráfico de red.
- **En Modo Solo API:** Puedes verificar la recepción directamente consultando la base de datos en MySQL:
  ```sql
  SELECT * FROM metrics ORDER BY ts DESC LIMIT 10;
  ```
