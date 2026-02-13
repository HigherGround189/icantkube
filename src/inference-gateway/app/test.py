import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
# Check if a specific registered model exists
try:
    client.get_registered_model("model_name")
    print("Model exists")
except:
    print("Model does not exist")
