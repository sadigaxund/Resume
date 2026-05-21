#!/usr/bin/env bash
# Archive current PDF with timestamp suffix and commit to git.

set -e

cd "$(dirname "$0")/.."

PDF="SadigAkhund_Resume.pdf"
if [[ ! -f "$PDF" ]]; then
    echo "!! $PDF not found. Build first."
    exit 1
fi

mkdir -p Archive

TIMESTAMP=$(date +%Y-%m-%d)
ARCHIVED="Archive/SadigAkhund_Resume_${TIMESTAMP}.pdf"

cp "$PDF" "$ARCHIVED"
echo ">> Archived: $ARCHIVED"

git add "$ARCHIVED" "$PDF" SadigAkhund_Resume.tex 2>/dev/null || true
git add -A

if git diff --cached --quiet; then
    echo ">> Nothing to commit."
    exit 0
fi

MSG="${1:-Version snapshot $TIMESTAMP}"
git commit -m "$MSG"
git push

echo ">> Committed and pushed: $MSG"
