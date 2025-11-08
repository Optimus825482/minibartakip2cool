# Python 3.11 slim image kullan (güvenlik ve boyut için)
FROM python:3.11-slim

# Metadata
LABEL maintainer="Erkan"
LABEL description="Minibar Takip Sistemi - Docker Container"

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (MySQL client ve güvenlik güncellemeleri)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Entrypoint script'ini executable yap
RUN chmod +x docker-entrypoint.sh

# Güvenlik: Non-root user oluştur
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Port expose et
EXPOSE 8080

# Health check ekle
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Entrypoint ve CMD
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
