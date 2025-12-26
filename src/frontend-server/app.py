from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/api/{count}")
def echo(count: int):
    if count == 0:
        return {"message": "Press those other buttons too!"}
    elif count > 0:
        return {"message": "You're a positive man!"}
    else:
        return {"message": "You're a negative man!"}

app.mount(
    "/", 
    StaticFiles(directory="dist", html=True), 
    name="vite"
)