import mlflow
from mlflow.tracking import MlflowClient
import mlflow.sklearn

# Set the MLflow tracking URI if it's not already set by an environment variable
# mlflow.set_tracking_uri("http://your-mlflow-server.com")

client = MlflowClient()

model_name = "Wittman"

try:
    # Get the latest version(s) of the registered model
    latest_versions = client.get_latest_versions(model_name, stages=["None", "Staging", "Production", "Archived"]) # Get versions from all stages
    
    if latest_versions:
        # The first item in the list is typically the latest (based on creation time if not ordered otherwise)
        # To be absolutely sure about the *latest creation*, you might need to sort.
        # However, client.get_latest_model_versions often handles this implicitly.
        # Let's get the version object directly
        latest_version_details = latest_versions[0]
        run_id = latest_version_details.run_id
        
        print(f"The latest run ID for model '{model_name}' is: {run_id}")
    else:
        print(f"No versions found for model '{model_name}'.")

except Exception as e:
    print(f"Error accessing model registry: {e}")

latest_version = latest_versions[0].version
model_uri = f"runs:/{run_id}/{latest_version}"
model = mlflow.sklearn.load_model(model_uri)
print("Model loaded")

predictions = model.predict({"5.4","3.4","1.5","0.4","setosa"})
print(predictions)
