# =====================================================================
# BLOCK: DOCKER IMAGE (Dockerfile)
# ---------------------------------------------------------------------
# Builds a container that runs the dashboard.
#
# FIXES vs the previous version:
#   1. The CV files (data/) are NO LONGER baked into the image. They
#      contain personal information (names, phones, emails) and must
#      not travel inside an image you might push to a registry. The
#      folder is attached at runtime instead (see docker-compose.yml).
#   2. The old HEALTHCHECK used `curl`, which is not installed in the
#      python:slim image — so the container always reported "unhealthy".
#      Python itself performs the check now.
# =====================================================================
FROM python:3.11-slim

WORKDIR /app

# System dependencies for OCR (reading scanned CVs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ara \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .streamlit/ ./.streamlit/

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
