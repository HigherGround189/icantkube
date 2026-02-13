from pydantic import BaseModel

class CreateServer(BaseModel):
    model_name: str
    replicas: int = 1
    prediction_interval: int = 5
    