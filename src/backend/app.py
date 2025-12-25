from fastapi import FastAPI

app = FastAPI()

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

