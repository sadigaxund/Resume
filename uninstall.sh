#!/usr/bin/env bash
set -e

SERVICE_NAME="resume-server"

SERVICE_FILE="${HOME}/.config/systemd/user/${SERVICE_NAME}.service"
INSTALL_DIR=""

if [ -f "$(dirname "$0")/server.py" ] 2>/dev/null; then
  INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

echo ">> Stopping and disabling service..."
systemctl --user disable --now "${SERVICE_NAME}" 2>/dev/null || true

if [ -f "$SERVICE_FILE" ]; then
  rm -f "$SERVICE_FILE"
  echo ">> Removed service file: ${SERVICE_FILE}"
  systemctl --user daemon-reload
fi

if [ -n "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR" ]; then
  if [ -t 0 ]; then
    echo ""
    read -r -p ">> Remove source directory ${INSTALL_DIR}? [y/N]: " REPLY
    if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
      rm -rf "$INSTALL_DIR"
      echo ">> Removed: ${INSTALL_DIR}"
    fi
  fi
fi

echo ">> Done. Service '${SERVICE_NAME}' has been removed."
