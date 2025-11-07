# Prometheus Monitoring Setup

## Deskripsi

Setup monitoring untuk MLflow model menggunakan Prometheus dan Grafana. Sistem ini memantau performa API model termasuk jumlah request, latensi, penggunaan CPU, dan RAM.

## Prasyarat

- Python 3.x
- Docker
- Prometheus
- Grafana
- Dependencies: `pip install flask requests psutil prometheus_client`

## Langkah-langkah Setup

### 1. Jalankan ML Model dengan Docker

```bash
docker run -d -p 5005:8080 lukaskrisna/credit-scoring-model-optimized
```

### 2. Jalankan Prometheus Exporter

```bash
cd prometheus-monitoring
python prometheus_exporter.py
```

Server akan berjalan di `http://127.0.0.1:8000`

### 3. Test Endpoint

#### Test dengan cURL

**Test /metrics endpoint:**

```bash
curl http://127.0.0.1:8000/metrics
```

**Test /predict endpoint:**

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_split": {
      "columns": ["feature1", "feature2"],
      "data": [[1.0, 2.0]]
    }
  }'
```

#### Test dengan Postman

1. **GET** `http://127.0.0.1:8000/metrics`

   - Headers: None required

2. **POST** `http://127.0.0.1:8000/predict`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "dataframe_split": {
       "columns": [
         "Age",
         "Credit_Mix",
         "Payment_of_Min_Amount",
         "Payment_Behaviour",
         "pc1_1",
         "pc1_2",
         "pc1_3",
         "pc1_4",
         "pc1_5",
         "pc2_1",
         "pc2_2"
       ],
       "data": [
         [
           0.7142857142857142, 1, 1, 3, -0.4381534490735855, 0.1711382783346808,
           0.0773630019922211, -0.0401910461904993, 0.049590092121234,
           -0.1448249280763024, -0.0606673847105827
         ],
         [
           0.4523809523809524, 2, 2, 5, 0.4778277065736656, -0.1050643177401745,
           -0.185971337955209, -0.3789896489656689, 0.1718128833126148,
           -0.2417658875286998, 0.0066502389514661
         ],
         [
           0.4999999999999999, 3, 1, 1, -0.2172441359177029, 0.0068230171993729,
           0.0319554863404481, -0.0402970285419156, 0.0861914654821804,
           0.779882880094656, 0.1309092693530689
         ],
         [
           0.4523809523809524, 1, 1, 6, -0.6893954147621222, 0.1842207645520866,
           0.1887210184373613, -0.1923419820570049, 0.0561499495340574,
           0.5840348959263311, 0.0673148184570155
         ],
         [
           0.8333333333333333, 3, 0, 5, -0.287145204288708, -0.2462885871184559,
           0.1247759677401836, -0.0544947505767573, 0.0941141473487672,
           0.0526512725593595, -0.1827263807556981
         ]
       ]
     }
   }
   ```

### 4. Setup Prometheus

1. **Buat file `prometheus.yml`:**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "mlflow-model"
    static_configs:
      - targets: ["127.0.0.1:8000"]
```

2. **Jalankan Prometheus:**

```bash
# Download Prometheus jika belum ada
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.darwin-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Jalankan dengan config file
./prometheus --config.file=prometheus.yml --storage.tsdb.path=./data
```

Prometheus UI: `http://localhost:9090`

### 5. Setup Grafana

1. **Install Grafana:**

```bash
# macOS dengan Homebrew
brew install grafana
brew services start grafana

# Atau dengan Docker
docker run -d -p 3000:3000 grafana/grafana
```

2. **Login ke Grafana:**

   - URL: `http://localhost:3000`
   - Username: `admin`
   - Password: `admin`

3. **Tambahkan Data Source:**
   - Go to Configuration > Data Sources
   - Add data source > Prometheus
   - URL: `http://localhost:9090`
   - Save & Test

### 6. Buat Dashboard di Grafana

1. **Buat Dashboard Baru:**

   - Go to Create > Dashboard
   - Add new panel

2. **Tambahkan Panel dengan Query:**

   **Panel 1 - Total Requests:**

   - Query: `http_requests_total`
   - Title: "Total API Requests"
   - Type: Stat

   **Panel 2 - API Latency (95th percentile):**

   - Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
   - Title: "API Latency (95th percentile)"
   - Type: Time series
   - Unit: seconds

   **Panel 3 - CPU Usage:**

   - Query: `system_cpu_usage`
   - Title: "CPU Usage (%)"
   - Type: Time series
   - Unit: percent (0-100)

   **Panel 4 - RAM Usage:**

   - Query: `system_ram_usage`
   - Title: "RAM Usage (%)"
   - Type: Time series
   - Unit: percent (0-100)

### 7. Test Load untuk Generate Metrics

Buat script sederhana untuk generate load:

```bash
# Generate beberapa request
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"dataframe_split": {"columns": ["feature1"], "data": [[1.0]]}}' &
done
wait
```

## Monitoring Queries

Berikut query yang bisa digunakan di Prometheus/Grafana:

```promql
# Total request API model
http_requests_total

# Latensi API model (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Penggunaan CPU server
system_cpu_usage

# Penggunaan RAM server
system_ram_usage

# Request rate (per second)
rate(http_requests_total[5m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

## Troubleshooting

1. **Model tidak respond:**

   - Pastikan Docker container berjalan: `docker ps`
   - Check logs: `docker logs <container_id>`

2. **Prometheus tidak scrape:**

   - Verify targets di `http://localhost:9090/targets`
   - Check prometheus.yml configuration

3. **Grafana tidak connect:**
   - Test data source connection
   - Verify Prometheus URL
