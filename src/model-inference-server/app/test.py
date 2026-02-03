import mlflow
import os
from mlflow.tracking import MlflowClient

client = MlflowClient()
print("Client initialised")

registered_models = client.search_registered_models()
print(registered_models)


# client = MlflowClient()
# model_name = "IrisPipelineModel"
# print("Client initialised")

# modles = client.search_registered_models()
# print(modles)
# # Retrieve details for a specific version
# model_version_details = client.get_model_version(name=model_name, version="1")
# # The 'source' attribute contains the full artifact URI
# model_uri = model_version_details.source 
# print(f"Model URI for version 1: {model_uri}")

# model = mlflow.pyfunc.load_model("models:/IrisPipelineModel/Version 1")
# print("Model loaded")

# predictions = model.predict({"5.4","3.4","1.5","0.4","setosa"})
# print(predictions)