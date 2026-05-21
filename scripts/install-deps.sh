#!/usr/bin/env bash
# Install LaTeX packages needed to compile SadigAkhund_Resume.tex on Fedora.
# Minimal — no full texlive-scheme-medium bundle.

set -e

PKGS=(
    texlive-latex
    texlive-xetex
    texlive-fontspec
    texlive-titlesec
    texlive-marvosym
    texlive-enumitem
    texlive-fancyhdr
    texlive-hyperref
    texlive-babel
    texlive-babel-english
    texlive-tools
    texlive-cm-super
    texlive-amsfonts
    texlive-ec
    texlive-metafont
    texlive-helvetic
    texlive-psnfss
    texlive-xcolor
    texlive-fontawesome5
    texlive-geometry
    texlive-needspace
    texlive-collection-fontsrecommended
)

echo ">> Installing LaTeX packages..."
sudo dnf install -y --skip-unavailable "${PKGS[@]}"

echo ">> Rebuilding PDF..."
"$(dirname "$0")/build.sh"

echo ">> Done."
