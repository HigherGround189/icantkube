import httpx
from fastapi import Request, HTTPException
from fastapi.responses import Response

async def forward_request(
    *,
    request: Request,
    target_url: str,
) -> Response:
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            headers=headers,
            content=await request.body(),
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp.headers,
    )
