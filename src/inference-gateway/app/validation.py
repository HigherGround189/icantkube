from pydantic import BaseModel

class CreateServer(BaseModel):
    model_name: str
    replicas: int = 1
    prediction_interval: int = 5

class DeleteServer(BaseModel):
    model_name: str

def check_if_model_is_registered_on_mlflow():
    pass

def check_if_deployment_exists():
    pass
