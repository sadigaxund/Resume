#!/usr/bin/env bash
set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <template.tex>"
  echo "Example: $0 template/Resume.tex"
  exit 1
fi

cd "$(dirname "$0")/.."

TEX_FILE="$1"
STEM=$(basename "$TEX_FILE" .tex)

echo ">> Cleaning aux files..."
rm -f "$STEM".aux "$STEM".log "$STEM".out \
      "$STEM".fls "$STEM".fdb_latexmk "$STEM".synctex.gz \
      "$STEM".xdv

echo ">> Compiling $TEX_FILE..."
latexmk -xelatex \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    -outdir=. \
    "$TEX_FILE"

echo ">> Built: ${STEM}.pdf"
