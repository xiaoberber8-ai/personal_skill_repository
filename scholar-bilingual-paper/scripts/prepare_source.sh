#!/usr/bin/env bash
# 用法: prepare_source.sh <paper.pdf> <outdir>
set -euo pipefail
PDF=${1:?usage: prepare_source.sh <paper.pdf> <outdir>}
OUT=${2:?usage: prepare_source.sh <paper.pdf> <outdir>}
command -v pdftotext >/dev/null || { echo "缺少 poppler-utils: apt install poppler-utils"; exit 1; }
mkdir -p "$OUT/pages" "$OUT/figures"
BASE="$OUT/$(basename "${PDF%.*}")"
pdftotext "$PDF" "${BASE}_raw.txt"
pdftotext -layout "$PDF" "${BASE}_layout.txt"
pdftoppm -png -r 150 "$PDF" "$OUT/pages/page"
echo "pages: $(find "$OUT/pages" -name 'page-*.png' | wc -l)"
echo "raw:   ${BASE}_raw.txt"
echo "layout:${BASE}_layout.txt"
