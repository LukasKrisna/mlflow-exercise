import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")
client = MlflowClient()

model_uri = f"runs:/68a91c645d914bdebc67835c4c78b07b/model"

client.create_model_version(
    name="credit-scoring",
    source=model_uri,
    run_id="68a91c645d914bdebc67835c4c78b07b"
)

