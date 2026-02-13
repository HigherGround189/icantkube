import mlflow
import numpy as np

model_name = "Wittman"

model_uri = f"models:/{model_name}/latest"
model = mlflow.sklearn.load_model(model_uri)

print("Model loaded")

X = np.array([[5.4, 3.4, 1.6]])
predictions = model.predict(X)

print(predictions)
