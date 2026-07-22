#!/usr/bin/env bash
set -e

REPO_URL=""

_read() {
  local var="$1" prompt="$2" default="$3"
  local val="${!var}"
  if [ -z "$val" ] && [ -c /dev/tty ]; then
    read -r -p ">> ${prompt} [${default}]: " val < /dev/tty
  fi
  eval "$var=\"${val:-$default}\""
}

_read HOST "Bind host (0.0.0.0 = all interfaces)" "0.0.0.0"
_read PORT "Bind port"                             "8000"
_read SVC  "Systemd service name"                  "resume-server"
echo ""

INSTALL_DIR="/opt/${SVC}"
LOCAL=""
if [ -f "$(dirname "$0")/app/server.py" ] 2>/dev/null; then
  LOCAL="yes"
  APP_DIR="$(cd "$(dirname "$0")/app" && pwd)"
fi

echo ">> Checking Python..."
PYTHON=$(command -v python3)
if [ -z "$PYTHON" ]; then
  echo "Error: python3 not found. Install it first."
  exit 1
fi

# ---------------------------------------------------------------------------
#  Repository URL
# ---------------------------------------------------------------------------
if [ -z "$REPO_URL" ]; then
  if [ -n "$LOCAL" ]; then
    REPO_URL=$(git remote get-url origin 2>/dev/null || true)
  fi
  if [ -z "$REPO_URL" ] && [ -n "$GITHUB_OWNER" ] && [ -n "$GITHUB_REPO" ]; then
    REPO_URL="https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}.git"
  fi
  if [ -z "$REPO_URL" ]; then
    _read REPO_URL "GitHub clone URL" ""
  fi
  if [ -z "$REPO_URL" ]; then
    echo "Error: could not determine repo URL."
    echo "Set GITHUB_OWNER and GITHUB_REPO env vars, or run from a git clone."
    exit 1
  fi
fi

# ---------------------------------------------------------------------------
#  Existing install detection & cleanup
# ---------------------------------------------------------------------------
SERVICE_FILE="/etc/systemd/system/${SVC}.service"
if [ -f "$SERVICE_FILE" ] || [ -d "$INSTALL_DIR" ]; then
  echo ">> Existing installation detected — stopping & removing..."
  sudo systemctl stop "${SVC}" 2>/dev/null || true
  sudo systemctl disable "${SVC}" 2>/dev/null || true
  sudo rm -f "$SERVICE_FILE"
  sudo systemctl daemon-reload
  sudo rm -rf "$INSTALL_DIR"
  echo ">> Old files removed."
fi

# ---------------------------------------------------------------------------
#  Fetch source
# ---------------------------------------------------------------------------
if [ -n "$LOCAL" ]; then
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
  sudo cp -r "${TMPDIR}/app" "$INSTALL_DIR/"
  rm -rf "$TMPDIR"
  APP_DIR="${INSTALL_DIR}/app"
fi

# ---------------------------------------------------------------------------
#  Virtualenv
# ---------------------------------------------------------------------------
echo ">> Creating Python virtual environment..."
if [ -n "$LOCAL" ]; then
  "$PYTHON" -m venv "${APP_DIR}/venv"
else
  sudo "$PYTHON" -m venv "${APP_DIR}/venv"
  sudo chown -R "$USER:" "${APP_DIR}/venv"
fi
"${APP_DIR}/venv/bin/pip" install -q -r "${APP_DIR}/requirements.txt"

# ---------------------------------------------------------------------------
#  Systemd service
# ---------------------------------------------------------------------------
echo ">> Creating systemd service..."
DESCRIPTION="Resume Server"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=${DESCRIPTION}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python -m uvicorn server:app --host ${HOST} --port ${PORT}
Restart=always
RestartSec=5
CPUQuota=50%
MemoryMax=256M
LimitNOFILE=1024

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "${SVC}"

echo ""
echo ">> Done! Service '${SVC}' is running on ${HOST}:${PORT}."
echo "   Status: sudo systemctl status ${SVC}"
echo "   Logs:   sudo journalctl -u ${SVC} -f"
