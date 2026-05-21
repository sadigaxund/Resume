#!/usr/bin/env bash
# Clean build artifacts and compile resume PDF.
# Non-interactive: halts on first error, never prompts.

set -e

cd "$(dirname "$0")/.."

echo ">> Cleaning aux files..."
rm -f SadigAkhund_Resume.aux SadigAkhund_Resume.log SadigAkhund_Resume.out \
      SadigAkhund_Resume.fls SadigAkhund_Resume.fdb_latexmk SadigAkhund_Resume.synctex.gz

echo ">> Compiling..."
latexmk -xelatex \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    SadigAkhund_Resume.tex

echo ">> Built: SadigAkhund_Resume.pdf"
