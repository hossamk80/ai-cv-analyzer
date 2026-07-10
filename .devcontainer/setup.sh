#!/usr/bin/env bash
# =====================================================================
# BLOCK: CODESPACES SETUP (.devcontainer/setup.sh)
# ---------------------------------------------------------------------
# Runs automatically when a Codespace is created or updated.
# Installs the OCR engine (for scanned CVs and images), antiword
# (for old .doc files) and the Python libraries.
#
# If the app ever shows "OCR engine (Tesseract) is not installed",
# run this by hand in the Codespace terminal:  bash .devcontainer/setup.sh
# =====================================================================
set -e

sudo apt-get update
sudo apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-ara antiword

pip3 install --user -r requirements.txt

echo "Setup complete: OCR engine, antiword and Python libraries installed."
