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
TEMPLATE=$(grep '^template:' template/resume.yml | sed 's/^template:[[:space:]]*//; s/"//g')
"$(dirname "$0")/build.sh" "template/$TEMPLATE"

echo ">> Done."
