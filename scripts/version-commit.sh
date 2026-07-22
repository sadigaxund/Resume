#!/usr/bin/env bash
set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <template.tex> [commit message]"
  echo "Example: $0 template/Resume.tex"
  exit 1
fi

cd "$(dirname "$0")/.."

TEX_FILE="$1"
STEM=$(basename "$TEX_FILE" .tex)
PDF="${STEM}.pdf"

if [ ! -f "$PDF" ]; then
    echo "!! $PDF not found. Build first: ./scripts/build.sh $TEX_FILE"
    exit 1
fi

mkdir -p Archive
DATE=$(date +%Y-%m-%d)
AUTHOR="${AUTHOR:-}"
AUTHOR_STEM=$(echo "$AUTHOR" | tr -d '[:space:]')
PREFIX="${AUTHOR_STEM:-$STEM}"
ARCHIVED="Archive/${PREFIX}_${DATE}.pdf"

cp "$PDF" "$ARCHIVED"
echo ">> Archived: $ARCHIVED"

git add "$ARCHIVED" "$PDF" "$TEX_FILE" 2>/dev/null || true
git add -A

if git diff --cached --quiet; then
    echo ">> Nothing to commit."
    exit 0
fi

MSG="${2:-Version snapshot $DATE}"
git commit -m "$MSG"
git push

echo ">> Committed and pushed: $MSG"
