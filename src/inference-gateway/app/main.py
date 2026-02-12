import logging
import kr8s.asyncio
from fastapi import FastAPI
from app.validation import CreateServer
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

app = FastAPI(title="Inference Gateway", redirect_slashes=False)
NAMESPACE = "model-pipeline"

@app.post("/inference/create-server")
async def create_server(server: CreateServer):
    logger.info(server.mlflow_name, server.replicas, server.prediction_interval)

@app.get("/inference/active-inference-servers")
async def get_inference_servers():
    deploy_list = []
    async for deploy in kr8s.asyncio.get("deployments", namespace=NAMESPACE):
        logger.info(deploy)
        deploy_list.append(deploy)

    return deploy_list

@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}
