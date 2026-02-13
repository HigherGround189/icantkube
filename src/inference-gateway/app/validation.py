from pydantic import BaseModel
from mlflow.tracking import MlflowClient
import kr8s

client = MlflowClient()

class CreateServer(BaseModel):
    model_name: str
    replicas: int = 1
    prediction_interval: int = 5

class DeleteServer(BaseModel):
    model_name: str

def model_is_on_mlflow(model_name: str):
    try:
        client.get_registered_model(model_name)
        return True
    except:
        return False

def inference_server_exists(model_name, namespace):
    deployment = kr8s.get("deployment", f"{model_name.lower()}-inference-server", namespace=namespace)

    return deployment.exists()
