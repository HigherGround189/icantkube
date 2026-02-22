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
    """
    Check whether a model is registered in MLflow.

    Args:
        model_name (str): Name of the MLflow registered model.

    Returns:
        bool: Returns True if the model exists in MLflow.
    """
    try:
        client.get_registered_model(model_name)
        logger.info(f"{model_name} found in Mlflow")
        return True
    except:
        logger.info(f"{model_name} not found in Mlflow")
        return False

async def inference_server_exists(model_name, namespace):
    """
    Check whether an inference server deployment already exists in Kubernetes.

    Args:
        model_name (str): Name of the inference server deployment.
        namespace (str): Kubernetes namespace to query.

    Returns:
        bool: Returns True if at least one matching deployment exists in the namespace.
    """
    deploy_list = [
        deploy.exists() async for deploy in kr8s.asyncio.get(
            "deployments", 
            f"{model_name.lower()}-inference-server", 
            namespace=namespace
        )
    ]

    logger.info(f"Deployment list: {deploy_list}")
    return any(deploy_list)
