import httpx
from fastapi import Request
from fastapi.responses import Response

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "content-encoding",
}

def sanitize_headers(headers):
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }

async def forward_request(
    *,
    request: Request,
    target_url: str,
) -> Response:
    outgoing_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            headers=outgoing_headers,
            content=await request.body(),
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=sanitize_headers(resp.headers),
    )
