#!/bin/sh
# Пересборка листов из исходного генплана (src/original) и расчётов (calc.py).
set -e
cd "$(dirname "$0")"
for b in main house sewer water power gas budget visual check; do python3 ${b}_board.py; done
python3 make_canvas.py
# PNG листов (нужен playwright + chromium): SCALE=1.5 node render.mjs ../canvas/project ../listy
