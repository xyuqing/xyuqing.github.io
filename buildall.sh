#!/usr/bin/env bash

shopt -s nullglob

PYTHON_SCRIPT="pybuilder/createhtml.py"

for file in ./html_modules/*.page; do
  echo "Processing file: $file"
  python3 "$PYTHON_SCRIPT" "$file"
done