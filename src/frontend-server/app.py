from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@app.get("/")
def index():
    from fastapi.responses import FileResponse
    return FileResponse("dist/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/{count}")
def echo(count: int):
    if count == 0:
        return {"message": "Press those other buttons too!"}
    elif count > 0:
        return {"message": "You're a positive man!"}
    else:
        return {"message": "You're a negative man!"}
