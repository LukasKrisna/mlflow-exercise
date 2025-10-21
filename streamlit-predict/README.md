# Credit Scoring Prediction with Streamlit and MLflow

## Deskripsi

Proyek ini menggunakan Streamlit untuk menyediakan antarmuka web untuk prediksi skor kredit menggunakan model machine learning yang disajikan melalui MLflow.

## Requirements

- Python 3.x
- MLflow
- Streamlit
- Python package yang diperlukan (misalnya: pandas, scikit-learn, joblib, numpy, requests)

## Instalasi

1. Navigasi ke direktori proyek.
2. Instal dependensi: `pip install mlflow streamlit pandas scikit-learn joblib numpy requests`

## Cara Menjalankan

1. Jalankan server MLflow:

   ```
   mlflow server --host 127.0.0.1 --port 5000
   ```

2. Serving model:

   ```
   mlflow models serve -m "models:/credit-scoring/1" --port 5002 --no-conda
   ```

3. Jalankan aplikasi Streamlit:

   Navigasi ke folder `streamlit-predict` dan jalankan:

   ```
   streamlit run app.py
   ```

4. Buka browser ke `http://localhost:8501` untuk menggunakan aplikasi.

## Catatan

- Pastikan model terdaftar di MLflow dengan nama "credit-scoring" dan versi 1.
- Aplikasi menggunakan `preprocessAPI.py` untuk preprocessing data dan prediksi.
