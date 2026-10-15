FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRAUD_SHIELD_DB=/data/shield.db

# XGBoost needs the OpenMP runtime, which the slim image does not include.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Run as an unprivileged user; the database lives on a volume.
RUN useradd --create-home --uid 10001 app && mkdir /data && chown app /data
USER app
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"

# Model artifacts ship in the image; run.py trains one only if they are missing.
CMD ["python", "run.py", "--host", "0.0.0.0", "--no-browser"]
