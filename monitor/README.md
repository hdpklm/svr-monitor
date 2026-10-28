# Monitor

Lee métricas del servidor 20 veces por segundo y envía cada minuto la media, el mínimo y el máximo a un endpoint HTTP.

## Métricas

**Rápidas (20 por segundo, con media, mín y máx)**
- `cpu_percent`
- `ram_percent`, `ram_used_mb`
- `net_rx_kbps`, `net_tx_kbps`
- `disk_read_mbps`, `disk_write_mbps`

**Lentas (1 por minuto)**
- `load1`, `swap_percent`, `uptime_s`
- `disk_used_percent` por ruta
- `cpu_temp_c` (si existe sensor)

## Archivos

| Archivo | Función |
|---|---|
| `setup.sh` | Instala y arranca el servicio |
| `config.py` | Ajustes |
| `collector.py` | Lee las métricas |
| `aggregator.py` | Calcula media, mín y máx |
| `sender.py` | Envía por HTTP y reintenta |
| `main.py` | Bucle principal |
| `monitor.service` | Servicio systemd |

## Instalación

Copia la carpeta al servidor y ejecuta:

```bash
sudo bash setup.sh
```

Pregunta la URL del endpoint y la API key. La clave no se muestra al escribirla.

También acepta argumentos (la clave queda en el historial de la terminal):
```bash
sudo bash setup.sh https://tu-servidor/api/metrics tu_clave nombre-del-servidor
```

El nombre del servidor es opcional. Por defecto usa el hostname.

**Qué hace `setup.sh`**
1. Instala uv si no existe.
2. Crea el usuario de sistema `monitor` (sin shell ni permisos).
3. Copia los archivos a `/srv/monitor`.
4. Crea el entorno `venv` e instala las dependencias.
5. Guarda la URL y la clave en `/srv/monitor/.env` (permisos 600).
6. Instala el servicio `monitor`, lo activa al arrancar el sistema y lo inicia.

## Comprobar

```bash
systemctl status monitor
journalctl -u monitor -f
```

## Gestionar el servicio

```bash
sudo systemctl restart monitor
sudo systemctl stop monitor
sudo systemctl disable --now monitor
```

## Actualizar

Copia los archivos nuevos y vuelve a ejecutar:
```bash
sudo bash setup.sh
```

Sin argumentos conserva el `.env` actual. Sobrescribe `config.py`, así que cambia los ajustes en el `config.py` de la carpeta de origen.

## Configuración

En `config.py`:

| Variable | Valor | Descripción |
|---|---|---|
| `SAMPLE_HZ` | 20 | Lecturas por segundo |
| `WINDOW_SECONDS` | 60 | Segundos entre envíos |
| `DISK_PATHS` | `["/"]` | Rutas a vigilar |
| `SEND_TIMEOUT` | 10 | Timeout del envío en segundos |
| `MAX_PENDING` | 120 | Envíos pendientes guardados si falla la red |

## Formato del envío

`POST` a `MONITOR_URL` con la cabecera `X-API-Key`.

```json
{
	"host": "servidor1",
	"timestamp": "2026-10-28T18:53:00+00:00",
	"window_seconds": 60,
	"samples": 1200,
	"metrics": {
		"cpu_percent": {"avg": 3.2, "min": 0.0, "max": 41.5},
		"ram_percent": {"avg": 47.1, "min": 46.9, "max": 47.4}
	},
	"slow": {
		"load1": 0.15,
		"swap_percent": 0.0,
		"disk_used_percent": {"/": 28.3},
		"uptime_s": 86400,
		"cpu_temp_c": 52.0
	}
}
```

El `timestamp` está en UTC.

## Fallos de red

Si el servidor no responde (error de red, 5xx, 408 o 429), el envío se guarda y se reintenta con el siguiente. Se guardan como máximo `MAX_PENDING` envíos. Un error 4xx se descarta.
