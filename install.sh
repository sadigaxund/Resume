#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/sadigaxund/Resume.git"
SERVICE_NAME="resume-server"

if [ -f "$(dirname "$0")/server.py" ] 2>/dev/null; then
  INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
else
  INSTALL_DIR="${HOME}/Resume"
  echo ">> Cloning repo into ${INSTALL_DIR}..."
  if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR" && git pull
  else
    git clone "$REPO_URL" "$INSTALL_DIR"
  fi
fi

cd "$INSTALL_DIR"

echo ">> Checking Python..."
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 not found. Install it first."
  exit 1
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

echo ">> Installing Python dependencies..."
pip3 install --user -q fastapi uvicorn httpx

echo ">> Creating systemd user service..."
mkdir -p "${HOME}/.config/systemd/user"

cat > "${HOME}/.config/systemd/user/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Resume Server — Sadig Akhund
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=$(command -v python3) -m uvicorn server:app --host ${HOST} --port ${PORT}
Restart=always
RestartSec=5
Environment=PORT=${PORT}

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "${SERVICE_NAME}"
loginctl enable-linger "$USER" 2>/dev/null || true

echo ">> Done! Service '${SERVICE_NAME}' is running on ${HOST}:${PORT}."
echo "   Status: systemctl --user status ${SERVICE_NAME}"
echo "   Logs:   journalctl --user -u ${SERVICE_NAME} -f"
