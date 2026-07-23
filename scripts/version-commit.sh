#!/usr/bin/env bash
set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <template.tex> [commit message]"
  echo "Example: $0 template/Template_Resume.tex"
  exit 1
fi

cd "$(dirname "$0")/.."

TEX_FILE="$1"
STEM=$(basename "$TEX_FILE" .tex)

OUTPUT=$(grep '^output:' template/resume.yml 2>/dev/null | sed 's/^output:[[:space:]]*//; s/"//g')
[ -z "$OUTPUT" ] && OUTPUT="$STEM"
PDF="${OUTPUT}.pdf"

if [ ! -f "$PDF" ]; then
    STEM2=$(basename "$TEX_FILE" .tex)
    if [ -f "${STEM2}.pdf" ]; then
        cp "${STEM2}.pdf" "$PDF"
    else
        echo "!! $PDF not found. Build first: ./scripts/build.sh $TEX_FILE"
        exit 1
    fi
fi

mkdir -p Archive
DATE=$(date +%Y-%m-%d)
ARCHIVED="Archive/${OUTPUT}_${DATE}.pdf"

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
