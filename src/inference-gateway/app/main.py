import logging
import kr8s.asyncio
from fastapi import FastAPI
from app.validation import CreateServer, DeleteServer, check_if_deployment_exists
from app.resource_templates import template_deployment
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

app = FastAPI(title="Inference Gateway", redirect_slashes=False)
NAMESPACE = "model-pipeline"

@app.post("/inference/create-server")
async def create_server(server: CreateServer):
    logger.info(server.model_name, server.replicas, server.prediction_interval)
    deployment = template_deployment(server.model_name.lower(), server.replicas, server.prediction_interval)
    deployment.create()

    return {
        "message": "Created deployment with the following parameters",
        "Model Name": server.model_name,
        "Replicas": server.replicas,
        "Prediction Interval": server.prediction_interval
        }

@app.post("/inference/delete-server")
async def delete_server(server: DeleteServer):
    logger.info(server.model_name)
    check_if_deployment_exists()
    deployment = kr8s.asyncio.get("deployment", f"{server.model_name.lower()}-inference-server")
    deployment.delete()
    

@app.get("/inference/active-inference-servers")
async def get_inference_servers():
    deploy_list = []
    async for deploy in kr8s.asyncio.get("deployments", namespace=NAMESPACE):
        logger.info(dir(deploy), deploy)
        deploy_list.append(deploy)

    return deploy_list

@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}
