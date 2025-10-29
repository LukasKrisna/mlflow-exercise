import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np

# Simulasi dataset
X = np.random.rand(500, 5)
y = np.random.randint(0, 2, size=(500,))

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Melatih model baru
model = LogisticRegression()
model.fit(X_train, y_train)

# Memprediksi hasil
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# Menyimpan model ke MLflow Tracking
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("model_redeployment")

with mlflow.start_run():
    mlflow.sklearn.log_model(model, "logistic_regression_model")
    mlflow.log_metric("accuracy", accuracy)
    print(f"Model disimpan dengan accuracy: {accuracy}")