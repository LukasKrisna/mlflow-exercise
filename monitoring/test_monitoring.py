import requests
import json
import time
import logging

# Konfigurasi logging
logging.basicConfig(filename="api_model_logs.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Endpoint API model
API_URL = "http://127.0.0.1:5004/invocations"

# Contoh input untuk model (ubah sesuai dengan kebutuhan model)
input_data = {"dataframe_split": {
    "columns": ["Age", "Credit_Mix", "Payment_of_Min_Amount", "Payment_Behaviour", "pc1_1", "pc1_2", "pc1_3", "pc1_4",
                "pc1_5", "pc2_1", "pc2_2"], "data": [
        [0.21428571428571425, 1.0, 1.0, 5.0, -0.37468239014988336, 0.32285307489248416, 0.03363800859809574,
         0.1345017413708082, 0.008756531181056654, -0.20887191599368923, -0.07916162364082943]]}}

# Konversi data ke JSON
headers = {"Content-Type": "application/json"}
payload = json.dumps(input_data)

# Mulai mencatat waktu eksekusi
start_time = time.time()

try:
    # Kirim request ke API
    response = requests.post(API_URL, headers=headers, data=payload)

    # Hitung response time
    response_time = time.time() - start_time

    if response.status_code == 200:
        prediction = response.json()  # Ambil hasil prediksi

        # Logging hasil request
        logging.info(f"Request: {input_data}, Response: {prediction}, Response Time: {response_time:.4f} sec")

        print(f"Prediction: {prediction}")
        print(f"Response Time: {response_time:.4f} sec")
    else:
        logging.error(f"Error {response.status_code}: {response.text}")
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    logging.error(f"Exception: {str(e)}")
    print(f"Exception: {str(e)}")