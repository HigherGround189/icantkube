from fastapi import FastAPI
import mlflow
import os

mlflow.set_tracking_uri("http://mlflow.icantkube.help/")

MODEL = os.getenv("MODEL_NAME")
app = FastAPI(title=f"{MODEL} Inference Server", redirect_slashes=False)


@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}
