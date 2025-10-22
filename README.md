# Credit Scoring Prediction with Streamlit and MLflow (Docker Deployment)

## Deskripsi

Proyek ini menggunakan Streamlit untuk menyediakan antarmuka web untuk prediksi skor kredit menggunakan model machine learning yang disajikan melalui MLflow. Guide ini mencakup deployment menggunakan Docker untuk production-ready environment.

## Requirements

### Development
- Python 3.x
- MLflow
- Streamlit
- Python packages: pandas, scikit-learn, joblib, numpy, requests

### Production (Docker)
- Docker Desktop atau Docker Engine
- MLflow (untuk generate Dockerfile)

## Instalasi

### Mode Development (Tanpa Docker)

1. Navigasi ke direktori proyek.
2. Instal dependensi:
   ```bash
   pip install mlflow streamlit pandas scikit-learn joblib numpy requests
   ```

### Mode Production (Dengan Docker)

1. Pastikan Docker sudah terinstal dan berjalan
2. Pastikan model sudah terdaftar di MLflow dengan nama "credit-scoring" dan versi 1

## Cara Menjalankan

### Opsi 1: Development Mode (Tanpa Docker)

#### 1. Jalankan MLflow Server
```bash
mlflow server --host 127.0.0.1 --port 5000
```

#### 2. Serving Model
```bash
mlflow models serve -m "models:/credit-scoring/1" --port 5002 --no-conda
```

#### 3. Jalankan Aplikasi Streamlit
Navigasi ke folder `streamlit-predict` dan jalankan:
```bash
streamlit run app.py
```

#### 4. Akses Aplikasi
Buka browser ke `http://localhost:8501`

---

### Opsi 2: Production Mode (Dengan Docker)

#### 1. Generate Dockerfile dari MLflow Model
```bash
mlflow models generate-dockerfile -m models:/credit-scoring/1
```

Perintah ini akan membuat `Dockerfile` dan folder `model_dir/` di dalam direktori `mlflow-dockerfile` secara otomatis.

#### 2. Optimasi Dockerfile (Opsional tapi Disarankan)

Edit `Dockerfile` yang telah di-generate untuk optimasi performa:

```dockerfile
# Build stage - includes build tools
FROM python:3.12.7-slim AS builder

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mlflow

# Install MLflow
RUN pip install --no-cache-dir mlflow==2.18.0

# Copy model and install dependencies
COPY model_dir/ /opt/ml/model
RUN python -c "from mlflow.models import container as C; C._install_pyfunc_deps('/opt/ml/model', install_mlflow=False, enable_mlserver=False, env_manager='local');"

# Runtime stage - minimal image without build tools
FROM python:3.12.7-slim

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mlflow

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /opt/ml/model /opt/ml/model

ENV MLFLOW_DISABLE_ENV_CREATION=True
ENV ENABLE_MLSERVER=False

# Optimize Gunicorn for lower CPU usage
ENV GUNICORN_CMD_ARGS="--timeout 60 --workers 2 --threads 2 --worker-class sync --max-requests 1000 --max-requests-jitter 50 --worker-tmp-dir /dev/shm"

# Limit Python's CPU usage
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

RUN chmod o+rwX /opt/mlflow/

ENTRYPOINT ["python", "-c", "from mlflow.models import container as C; C._serve('local')"]
```

#### 3. Build Docker Image
```bash
docker build -t testing-credit-scoring:v1 .
```

**Catatan:** Proses build mungkin memakan waktu 5-10 menit tergantung spesifikasi komputer.

#### 4. Run Docker Container

**Mode Foreground (untuk testing):**
```bash
docker run --name="Credit-scoring" -p 5004:8080 testing-credit-scoring:v1
```

**Mode Detached (untuk production):**
```bash
docker run -d --name="Credit-scoring-detach" -p 5004:8080 testing-credit-scoring:v1
```

**Mode Detached dengan Resource Limits (Recommended):**
```bash
docker run -d \
  --name="Credit-scoring-detach" \
  --cpus="2" \
  --memory="2g" \
  --memory-swap="2g" \
  -p 5004:8080 \
  testing-credit-scoring:v1
```

#### 5. Test Model Endpoint

**Menggunakan curl:**
```bash
curl -X POST http://127.0.0.1:5004/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_split": {
      "columns": ["feature1", "feature2", "feature3"],
      "data": [[value1, value2, value3]]
    }
  }'
```

**Menggunakan Python:**
```python
import requests
import json

url = "http://127.0.0.1:5004/invocations"
headers = {"Content-Type": "application/json"}
data = {
    "dataframe_split": {
        "columns": ["feature1", "feature2", "feature3"],
        "data": [[value1, value2, value3]]
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

#### 6. Jalankan Streamlit (Terhubung ke Docker Container)

Update `app.py` untuk mengarah ke Docker endpoint:
```python
# Ganti endpoint dari:
# API_URL = "http://localhost:5002/invocations"
# Menjadi:
API_URL = "http://localhost:5004/invocations"
```

Kemudian jalankan Streamlit:
```bash
cd streamlit-predict
streamlit run app.py
```

Akses aplikasi di `http://localhost:8501`

---

## Docker Commands Cheat Sheet

### Melihat Container yang Berjalan
```bash
docker ps
```

### Melihat Semua Container (termasuk yang stopped)
```bash
docker ps -a
```

### Melihat Logs Container
```bash
docker logs Credit-scoring-detach
```

### Melihat Logs Secara Real-time
```bash
docker logs -f Credit-scoring-detach
```

### Stop Container
```bash
docker stop Credit-scoring-detach
```

### Start Container yang Sudah Ada
```bash
docker start Credit-scoring-detach
```

### Remove Container
```bash
docker rm Credit-scoring-detach
```

### Remove Image
```bash
docker rmi testing-credit-scoring:v1
```

### Masuk ke Container (untuk debugging)
```bash
docker exec -it Credit-scoring-detach /bin/bash
```

### Monitoring Resource Usage
```bash
docker stats Credit-scoring-detach
```

---

## Opsi 3: Streamlit dengan Docker (Full Docker Deployment)

### Struktur Project
```
project/
├── Dockerfile.mlflow          # MLflow model serving
├── Dockerfile.streamlit        # Streamlit app
├── docker-compose.yml          # Orchestration
├── model_dir/                  # MLflow model files
└── streamlit-predict/
    ├── app.py
    └── preprocessAPI.py
```

### 1. Buat Dockerfile untuk Streamlit

**Dockerfile.streamlit:**
```dockerfile
FROM python:3.12.7-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    numpy \
    requests

# Copy application files
COPY streamlit-predict/ .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Buat docker-compose.yml

```yaml
version: '3.8'

services:
  mlflow-model:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: credit-scoring-model
    ports:
      - "5004:8080"
    environment:
      - GUNICORN_CMD_ARGS=--timeout 60 --workers 2 --threads 2 --worker-class sync
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - credit-scoring-network

  streamlit-app:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: credit-scoring-streamlit
    ports:
      - "8501:8501"
    environment:
      - MODEL_ENDPOINT=http://mlflow-model:8080/invocations
    depends_on:
      - mlflow-model
    networks:
      - credit-scoring-network

networks:
  credit-scoring-network:
    driver: bridge
```

### 3. Update app.py untuk Docker Environment

```python
import os

# Gunakan environment variable untuk endpoint
MODEL_ENDPOINT = os.getenv('MODEL_ENDPOINT', 'http://localhost:5004/invocations')
```

### 4. Jalankan dengan Docker Compose

```bash
# Build dan run semua services
docker-compose up -d

# Lihat logs
docker-compose logs -f

# Stop semua services
docker-compose down

# Rebuild dan restart
docker-compose up -d --build
```

### 5. Akses Aplikasi

- **Streamlit UI:** http://localhost:8501
- **MLflow Model API:** http://localhost:5004/invocations

---

## Troubleshooting

### Error: "gcc failed: No such file or directory"
**Solusi:** Gunakan Dockerfile yang sudah dioptimasi dengan multi-stage build (lihat langkah 2)

### High CPU Usage (>1000%)
**Solusi:** 
- Gunakan resource limits saat run container
- Pastikan menggunakan `--workers 2` di Gunicorn config
- Monitor dengan `docker stats`

### Container Immediately Stops
**Solusi:**
```bash
# Lihat logs untuk error
docker logs Credit-scoring-detach

# Cek apakah port sudah digunakan
docker ps -a
```

### Cannot Connect to Model API
**Solusi:**
```bash
# Test endpoint langsung
curl http://127.0.0.1:5004/health

# Pastikan container berjalan
docker ps

# Cek logs
docker logs Credit-scoring-detach
```

### Out of Memory Error
**Solusi:**
```bash
# Increase memory limit
docker run -d --name="Credit-scoring-detach" \
  --memory="4g" \
  -p 5004:8080 \
  testing-credit-scoring:v1
```

---

## Best Practices untuk Production

1. **Gunakan Resource Limits:** Selalu set CPU dan memory limits
2. **Health Checks:** Implementasi health check endpoint
3. **Logging:** Redirect logs ke external logging system
4. **Monitoring:** Gunakan tools seperti Prometheus + Grafana
5. **Backup Model:** Simpan model files di external storage
6. **CI/CD:** Automate build dan deployment dengan GitHub Actions/GitLab CI
7. **Security:** 
   - Jangan expose port secara public tanpa authentication
   - Gunakan HTTPS untuk production
   - Scan image untuk vulnerabilities: `docker scan testing-credit-scoring:v1`

---

## Catatan

- Pastikan model terdaftar di MLflow dengan nama "credit-scoring" dan versi 1 sebelum generate Dockerfile
- Port default MLflow model serving di container adalah 8080, di-map ke 5004 di host
- Aplikasi Streamlit menggunakan `preprocessAPI.py` untuk preprocessing data dan prediksi
- Untuk production, pertimbangkan menggunakan Docker Compose atau Kubernetes untuk orchestration
- Resource limits yang recommended: 2 CPU cores, 2GB RAM (adjust sesuai model size)

## Support

Jika mengalami masalah, silakan:
1. Cek logs: `docker logs <container-name>`
2. Monitor resources: `docker stats <container-name>`
3. Verify endpoint: `curl http://127.0.0.1:5004/health`