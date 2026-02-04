import kr8s.asyncio
from fastapi import FastAPI
from app.server import Server

app = FastAPI(title="Inference Gateway", redirect_slashes=False)
NAMESPACE = "inference"

@app.post("/inference/create-server")
async def create_server(server: Server):
    print(server.mlflow_name)

@app.get("/inference/active-inference-servers")
async def get_inference_servers():
    async for deploy in kr8s.asyncio.get("deployments", namespace=NAMESPACE):
        print(deploy)

@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}