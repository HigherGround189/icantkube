from pydantic import BaseModel

class Server(BaseModel):
    mlflow_name: str