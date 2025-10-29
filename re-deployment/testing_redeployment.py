import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np

# Menyimpan model ke MLflow Tracking
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("model_redeployment")

# Ambang batas untuk trigger re-deployment
THRESHOLD_ACCURACY = 0.85

# Simulasi dataset baru, harusnya diambil dari data baru atau gabungan.
X = np.random.rand(100, 20)
y = np.random.randint(0, 2, size=(100,))

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


def check_model_performance():
    """Memeriksa performa model terbaru dalam MLflow."""
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("model_redeployment")

    # Ambil semua run yang ada
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["metrics.accuracy DESC"])

    # Ambil model terbaru
    latest_model = runs[0]
    latest_accuracy = latest_model.data.metrics["accuracy"]

    print(f"Model existing memiliki accuracy: {latest_accuracy}")

    # Jika akurasi di bawah threshold, lakukan re-deployment
    if latest_accuracy < THRESHOLD_ACCURACY:
        print("Performa model turun! Memulai re-deployment...")
        retrain_and_deploy(latest_accuracy)
    else:
        print("Model masih dalam performa yang baik.")


def retrain_and_deploy(latest_accuracy):
    """Melatih ulang model dan menggantikan model lama jika lebih baik."""
    # Simulasi pelatihan ulang
    print("Melatih model baru...")
    new_model = LogisticRegression()
    new_model.fit(X_train, y_train)
    new_y_pred = new_model.predict(X_test)
    new_accuracy = accuracy_score(y_test, new_y_pred)

    # Bandingkan dengan model lama
    print(f"Model terbaru memiliki accuracy: {new_accuracy}")
    if new_accuracy > latest_accuracy:
        print(f"Model baru lebih baik, mengganti model lama ngenggg...")
        with mlflow.start_run():
            mlflow.sklearn.log_model(new_model, "logistic_regression_model")
            mlflow.log_metric("accuracy", new_accuracy)
    else:
        print("Model baru tidak lebih baik, tidak melakukan re-deployment.")


# Jalankan fungsi monitoring
check_model_performance()