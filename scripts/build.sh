#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo ">> Cleaning aux files..."
rm -f Template_Resumé.aux Template_Resumé.log Template_Resumé.out \
      Template_Resumé.fls Template_Resumé.fdb_latexmk Template_Resumé.synctex.gz \
      Template_Resumé.xdv

echo ">> Compiling..."
latexmk -xelatex \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    -outdir=. \
    template/Template_Resumé.tex

echo ">> Built: Template_Resumé.pdf"
