import kr8s.asyncio
from fastapi import FastAPI

app = FastAPI(title="Inference Gateway", redirect_slashes=False)


@app.get("/inference/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "health ok"}