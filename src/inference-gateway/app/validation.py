import kr8s
import logging
from pydantic import BaseModel
from mlflow.tracking import MlflowClient
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

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
        logger.info(f"{model_name} found in Mlflow")
        return True
    except:
        logger.info(f"{model_name} not found in Mlflow")
        return False

async def inference_server_exists(model_name, namespace):
    deploy_list = [
        deploy.exists() async for deploy in kr8s.asyncio.get(
            "deployments", 
            f"{model_name.lower()}-inference-server", 
            namespace=namespace
        )
    ]

    logger.info(f"Deployment list: {deploy_list}")
    return any(deploy_list)
