#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/srv/monitor"
SERVICE_NAME="monitor"
SERVICE_USER="monitor"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_FILES=(main.py config.py collector.py aggregator.py sender.py requirements.txt)

fail() {
	echo "error: $1" >&2
	exit 1
}

require_root() {
	[[ $EUID -eq 0 ]] || fail "ejecuta con sudo: sudo bash $0"
}

require_commands() {
	for name in curl systemctl; do
		command -v "$name" >/dev/null || fail "falta el comando $name"
	done
}

install_uv() {
	command -v uv >/dev/null && return
	curl -LsSf https://astral.sh/uv/install.sh | UV_UNMANAGED_INSTALL=/usr/local/bin sh
}

create_user() {
	id "$SERVICE_USER" &>/dev/null && return
	useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
}

copy_files() {
	mkdir -p "$INSTALL_DIR"
	for file in "${APP_FILES[@]}"; do
		[[ -f $SOURCE_DIR/$file ]] || fail "falta $file junto a setup.sh"
		install -m 644 "$SOURCE_DIR/$file" "$INSTALL_DIR/$file"
	done
}

create_venv() {
	uv venv --allow-existing --quiet "$INSTALL_DIR/venv"
	uv pip install --quiet --python "$INSTALL_DIR/venv/bin/python" -r "$INSTALL_DIR/requirements.txt"
}

write_env() {
	local url="${1:-${MONITOR_URL:-}}"
	local key="${2:-${MONITOR_API_KEY:-}}"
	local host="${3:-${MONITOR_HOST:-}}"
	local env_file="$INSTALL_DIR/.env"

	if [[ -f $env_file && -z $url && -z $key ]]; then
		echo "se mantiene $env_file"
		return
	fi

	if [[ -z $url ]]; then
		read -rp "URL del endpoint (https://.../api/metrics): " url
	fi
	if [[ -z $key ]]; then
		read -rsp "API key: " key
		echo
	fi
	[[ -n $url && -n $key ]] || fail "la URL y la API key son obligatorias"

	(
		umask 077
		{
			echo "MONITOR_URL=$url"
			echo "MONITOR_API_KEY=$key"
			if [[ -n $host ]]; then
				echo "MONITOR_HOST=$host"
			fi
		} > "$env_file"
	)
	chmod 600 "$env_file"
}

install_service() {
	install -m 644 "$SOURCE_DIR/monitor.service" "/etc/systemd/system/$SERVICE_NAME.service"
	systemctl daemon-reload
	systemctl enable "$SERVICE_NAME"
	systemctl restart "$SERVICE_NAME"
}

verify_service() {
	sleep 2
	if systemctl is-active --quiet "$SERVICE_NAME"; then
		echo "servicio activo"
		echo "logs: journalctl -u $SERVICE_NAME -f"
		return
	fi
	journalctl -u "$SERVICE_NAME" -n 20 --no-pager >&2
	fail "el servicio no arranca"
}

main() {
	require_root
	require_commands
	install_uv
	create_user
	copy_files
	create_venv
	write_env "$@"
	install_service
	verify_service
}

main "$@"
