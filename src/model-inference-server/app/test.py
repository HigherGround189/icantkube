import mlflow
import os
from mlflow.tracking import MlflowClient

client = MlflowClient()
print("Client initialised")

registered_models = client.search_registered_models()
print(registered_models)

model_name = "IrisPipelineModel"
model_version_details = client.get_model_version(name=model_name, version="1")
model_uri = model_version_details.source 
print(f"Model URI for version 1: {model_uri}")

model = mlflow.pyfunc.load_model(model_uri)
print("Model loaded")

predictions = model.predict({"5.4","3.4","1.5","0.4","setosa"})
print(predictions)
