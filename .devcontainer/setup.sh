#!/usr/bin/env bash
# =====================================================================
# BLOCK: CODESPACES SETUP (.devcontainer/setup.sh)
# ---------------------------------------------------------------------
# Runs automatically when a Codespace is created or updated.
# Installs the OCR engine (for scanned CVs and images), antiword
# (for old .doc files) and the Python libraries.
#
# IMPORTANT: this script must NEVER fail the container build. Each
# step tolerates its own errors (no `set -e`), so a temporary network
# hiccup while installing a package can't push the Codespace into
# "recovery mode". If a step fails, the app still starts; just re-run
# this script by hand in the terminal to finish the install:
#     bash .devcontainer/setup.sh
# =====================================================================

echo "==> Installing system packages (OCR + antiword)..."
sudo apt-get update || echo "WARN: apt-get update failed - continuing"
sudo apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-ara antiword \
    || echo "WARN: system package install failed - OCR/.doc may be unavailable"

echo "==> Installing Python libraries..."
pip3 install --user -r requirements.txt \
    || echo "WARN: pip install failed - run 'pip3 install --user -r requirements.txt' by hand"

echo "==> Setup finished."
exit 0
