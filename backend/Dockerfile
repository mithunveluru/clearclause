FROM python:3.13-slim

WORKDIR /app

# OCR system deps, shared by backend and worker
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
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
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
