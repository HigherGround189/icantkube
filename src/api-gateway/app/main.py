from fastapi import FastAPI, Request, HTTPException
from app.config import load_services
from app.gateway import forward_request

app = FastAPI(title="API Gateway")

SERVICES = load_services()

@app.api_route(
    "/api/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def api_gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Unknown service")

    base_url = SERVICES[service]["url"].rstrip("/")
    target_url = f"{base_url}/{path}"

    return await forward_request(
        request=request,
        target_url=target_url,
    )
