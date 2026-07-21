#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

PKGS=()
while IFS= read -r line; do
  line="${line%%#*}"        # strip comments
  line="${line//[[:space:]]/}"  # strip whitespace
  [[ -z "$line" ]] && continue
  PKGS+=("$line")
done < tex-packages.txt

echo ">> Installing LaTeX packages from tex-packages.txt..."
sudo dnf install -y --skip-unavailable "${PKGS[@]}"

echo ">> Rebuilding PDF..."
"$(dirname "$0")/build.sh"

echo ">> Done."
