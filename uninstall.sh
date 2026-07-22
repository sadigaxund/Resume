#!/usr/bin/env bash
set -e

SERVICE_NAME="resume-server"

if [ -f "$(dirname "$0")/app/server.py" ] 2>/dev/null; then
  INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
elif [ -d "/opt/${SERVICE_NAME}/app" ]; then
  INSTALL_DIR="/opt/${SERVICE_NAME}"
fi

echo ">> Stopping and disabling service..."
sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true

if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
  sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
  echo ">> Removed service file"
  sudo systemctl daemon-reload
fi

if [ -n "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR" ]; then
  if [ -t 0 ]; then
    echo ""
    read -r -p ">> Remove ${INSTALL_DIR}? [y/N]: " REPLY
    if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
      sudo rm -rf "$INSTALL_DIR"
      echo ">> Removed: ${INSTALL_DIR}"
    fi
  fi
fi

echo ">> Done. Service '${SERVICE_NAME}' has been removed."
