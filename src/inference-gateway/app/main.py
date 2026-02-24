import logging
import kr8s.asyncio
from fastapi import FastAPI
from app.validation import CreateServer, DeleteServer, model_is_on_mlflow, inference_server_exists
from app.resource_templates import template_deployment
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

app = FastAPI(title="Inference Gateway", redirect_slashes=False)
NAMESPACE = "model-pipeline"

@app.post("/inference/create-server")
async def create_server(server: CreateServer):
    """
    Communicates with the Kuberentes API Server to create a new Inference Server Deployment.

    Args:
        server (CreateServer): Request body containing:
            model_name (str): Name of the registered MLflow model.
            replicas (int): Number of deployment replicas.
            prediction_interval (int): Interval between predictions.

    Returns:
        dict: A dictionary containing:
            - message (str): Status message indicating result.
            - Model Name (str): Name of the model (if created).
            - Replicas (int): Number of replicas (if created).
            - Prediction Interval (int): Prediction interval (if created).
    """
    logger.info(f"Model Name: {server.model_name}, Replicas: {server.replicas}, Prediction Interval: {server.prediction_interval}")

    if model_is_on_mlflow(server.model_name) and await inference_server_exists(server.model_name, NAMESPACE) is False:
        deployment = template_deployment(server.model_name.lower(), server.replicas, server.prediction_interval)
        deployment.create()

        return {
            "message": "Created deployment with the following parameters",
            "Model Name": server.model_name,
            "Replicas": server.replicas,
            "Prediction Interval": server.prediction_interval
            }
    
    else:
        return {"message": "Can't create server, conditions not fulfilled"}

@app.post("/inference/delete-server")
async def delete_server(server: DeleteServer):
    """
    Communicates with the Kuberentes API Server to delete an existing Inference Server Deployment.

    Args:
        server (DeleteServer): Request body containing:
            model_name (str): Name of the model whose inference server should be deleted.

    Returns:
        dict: A dictionary containing:
            message (str): Confirmation message indicating which deployment was deleted.
    """
    logger.info(server.model_name)

    async for deploy in kr8s.asyncio.get("deployment", f"{server.model_name.lower()}-inference-server", namespace=NAMESPACE):
        logger.info(f"Deployment: {deploy}")
        await deploy.delete()
    
    return {"message": f"Deleted {server.model_name.lower()}-inference-server"}

@app.get("/inference/active-inference-servers")
async def get_inference_servers():
    """
    Retrieves all active inference server deployments.

    Returns:
        list: A list of Kubernetes deployment objects currently active in the namespace.
    """
    deploy_list = []
    async for deploy in kr8s.asyncio.get("deployments", namespace=NAMESPACE):
        logger.info(f"Deployment: {deploy}")
        deploy_list.append(deploy)

    return deploy_list

@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}
