#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/sadigaxund/Resume.git"
SERVICE_NAME="resume-server"
INSTALL_DIR="/opt/${SERVICE_NAME}"

if [ -f "$(dirname "$0")/app/server.py" ] 2>/dev/null; then
  LOCAL="yes"
else
  LOCAL=""
fi

if [ -t 0 ]; then
  read -r -p ">> Bind host [0.0.0.0]: " HOST
  HOST="${HOST:-0.0.0.0}"
  read -r -p ">> Bind port [8000]: " PORT
  PORT="${PORT:-8000}"
  echo ""
else
  HOST="${HOST:-0.0.0.0}"
  PORT="${PORT:-8000}"
fi

echo ">> Checking Python..."
PYTHON=$(command -v python3)
if [ -z "$PYTHON" ]; then
  echo "Error: python3 not found. Install it first."
  exit 1
fi

if [ -n "$LOCAL" ]; then
  APP_DIR="$(cd "$(dirname "$0")/app" && pwd)"
  echo ">> Using local app/ at ${APP_DIR}"
else
  if ! command -v git &>/dev/null; then
    echo "Error: git not found. Install git first."
    exit 1
  fi
  TMPDIR=$(mktemp -d)
  echo ">> Cloning repo (shallow)..."
  git clone --depth 1 "$REPO_URL" "$TMPDIR"
  sudo mkdir -p "$INSTALL_DIR"
  sudo rm -rf "${INSTALL_DIR}/app"
  sudo cp -r "${TMPDIR}/app" "$INSTALL_DIR/"
  rm -rf "$TMPDIR"
  APP_DIR="${INSTALL_DIR}/app"
fi

echo ">> Creating Python virtual environment..."
if [ -n "$LOCAL" ]; then
  "$PYTHON" -m venv "${APP_DIR}/venv"
else
  sudo "$PYTHON" -m venv "${APP_DIR}/venv"
  sudo chown -R "$USER:" "${APP_DIR}/venv"
fi
"${APP_DIR}/venv/bin/pip" install -q -r "${APP_DIR}/requirements.txt"

echo ">> Creating systemd service..."
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=Resume Server — Sadig Akhund
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python -m uvicorn server:app --host ${HOST} --port ${PORT}
Restart=always
RestartSec=5
Environment=PORT=${PORT}

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}"

echo ">> Done! Service '${SERVICE_NAME}' is running on ${HOST}:${PORT}."
echo "   Status: sudo systemctl status ${SERVICE_NAME}"
echo "   Logs:   sudo journalctl -u ${SERVICE_NAME} -f"
