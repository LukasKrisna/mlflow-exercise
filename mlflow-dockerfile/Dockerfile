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
# --workers: Limit to 2-4 workers instead of auto-scaling
# --threads: Use threading instead of gevent for better CPU efficiency
# --worker-class: sync is more CPU efficient than gevent for most cases
# --timeout: Keep at 60s
# --max-requests: Restart workers after N requests to prevent memory leaks
# --max-requests-jitter: Add randomness to prevent all workers restarting simultaneously
ENV GUNICORN_CMD_ARGS="--timeout 60 --workers 2 --threads 2 --worker-class sync --max-requests 1000 --max-requests-jitter 50 --worker-tmp-dir /dev/shm"

# Limit Python's CPU usage
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

RUN chmod o+rwX /opt/mlflow/

ENTRYPOINT ["python", "-c", "from mlflow.models import container as C; C._serve('local')"]