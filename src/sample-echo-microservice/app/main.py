from fastapi import FastAPI

app = FastAPI(title="sample-echo-microservice", redirect_slashes=False)

@app.get("/{msg}")
def echo(msg: str):
    return {"message": msg}


@app.get("/health")
def health():
    return {"status": "up"}