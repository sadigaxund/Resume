#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

PDF="Template_Resumé.pdf"
if [[ ! -f "$PDF" ]]; then
    echo "!! $PDF not found. Build first."
    exit 1
fi

mkdir -p Archive

TIMESTAMP=$(date +%Y-%m-%d)
ARCHIVED="Archive/Template_Resumé_${TIMESTAMP}.pdf"

cp "$PDF" "$ARCHIVED"
echo ">> Archived: $ARCHIVED"

git add "$ARCHIVED" "$PDF" template/Template_Resumé.tex 2>/dev/null || true
git add -A

if git diff --cached --quiet; then
    echo ">> Nothing to commit."
    exit 0
fi

MSG="${1:-Version snapshot $TIMESTAMP}"
git commit -m "$MSG"
git push

echo ">> Committed and pushed: $MSG"
