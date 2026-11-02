#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/hdpklm/svr-monitor.git"
REPO_TARBALL="https://github.com/hdpklm/svr-monitor/archive/refs/heads/main.tar.gz"
INSTALL_DIR="/srv/monitor"
SERVICE_NAME="monitor"
TMP_DIR=""
APP_FILES=(main.py config.py collector.py aggregator.py sender.py requirements.txt)

cleanup() {
	if [[ -n $TMP_DIR && -d $TMP_DIR ]]; then
		rm -rf "$TMP_DIR"
	fi
}
trap cleanup EXIT

fail() {
	echo "error: $1" >&2
	exit 1
}

step() {
	echo "==> $1"
}

require_root() {
	[[ $EUID -eq 0 ]] || fail "ejecuta con sudo: sudo bash $0"
}

download_latest() {
	step "[1/4] (25%) Descargando última versión desde GitHub..."
	TMP_DIR="$(mktemp -d)"
	if command -v git >/dev/null; then
		git clone --depth 1 --progress "$REPO_URL" "$TMP_DIR/repo"
	else
		mkdir -p "$TMP_DIR/repo"
		curl --progress-bar -fL "$REPO_TARBALL" | tar -xz -C "$TMP_DIR/repo" --strip-components=1
	fi
}

update_files() {
	step "[2/4] (50%) Actualizando archivos en $INSTALL_DIR..."
	local src="$TMP_DIR/repo/monitor"
	mkdir -p "$INSTALL_DIR"
	for file in "${APP_FILES[@]}"; do
		[[ -f "$src/$file" ]] || fail "falta $file en el repositorio"
		install -m 644 "$src/$file" "$INSTALL_DIR/$file"
	done
	if [[ -f "$src/update.sh" ]]; then
		install -m 755 "$src/update.sh" "$INSTALL_DIR/update.sh"
	fi
	if [[ -f "$src/monitor.service" ]]; then
		install -m 644 "$src/monitor.service" "/etc/systemd/system/$SERVICE_NAME.service"
		systemctl daemon-reload
	fi
}

update_deps() {
	step "[3/4] (75%) Sincronizando dependencias..."
	if command -v uv >/dev/null && [[ -d "$INSTALL_DIR/venv" ]]; then
		uv pip install --python "$INSTALL_DIR/venv/bin/python" -r "$INSTALL_DIR/requirements.txt"
	fi
}

restart_service() {
	step "[4/4] (100%) Reiniciando servicio $SERVICE_NAME..."
	systemctl restart "$SERVICE_NAME"
	sleep 2
	if systemctl is-active --quiet "$SERVICE_NAME"; then
		echo "✓ Monitor actualizado y activo"
		return
	fi
	journalctl -u "$SERVICE_NAME" -n 20 --no-pager >&2
	fail "el servicio no arranca tras actualizar"
}

main() {
	require_root
	download_latest
	update_files
	update_deps
	restart_service
}

main "$@"

