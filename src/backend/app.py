from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.icantkube.help"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/{count}")
def echo(count: int):
    message: str = ""
    if count == 0:
        message = "Press those other buttons too!"
    elif count > 0:
        message = "You're a positive man!"
    else:
        message = "You're a negative man!"

    return {"message": message}

