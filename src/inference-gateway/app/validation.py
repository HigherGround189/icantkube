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

async def inference_server_exists(model_name, namespace):
    deploy_list = [
        deploy.exists() async for deploy in kr8s.asyncio.get(
            "deployments", 
            f"{model_name.lower()}-inference-server", 
            namespace=namespace
        )
    ]

    return all(deploy_list)
