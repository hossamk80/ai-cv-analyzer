#!/usr/bin/env bash
# =====================================================================
# BLOCK: MAC/LINUX LAUNCHER (run.sh)
# ---------------------------------------------------------------------
# First time:  chmod +x run.sh
# Every time:  ./run.sh
# This file was referenced in the docs but never existed — added now.
# =====================================================================
set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
streamlit run src/dashboard.py
