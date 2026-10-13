FROM python:3.13-slim

WORKDIR /app

# OCR system deps, shared by backend and worker
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-tam \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Drop root; pre-create the storage dir for non-root writes
RUN useradd -m -u 1000 appuser \
    && mkdir -p /storage \
    && chown -R appuser:appuser /storage /app
USER appuser

EXPOSE 8000
# Render injects $PORT; compose does not
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
