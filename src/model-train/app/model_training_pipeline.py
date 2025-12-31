from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

import mlflow
try:
    print("Connecting to MLflow...")
    # mlflow.set_tracking_uri("https://mlflow.icantkube.help")
    mlflow.set_tracking_uri("http://localhost:5200") # local testing
    uri = mlflow.get_tracking_uri()
    experiments = mlflow.search_experiments()
    print(f"Connected to MLflow! Found {len(experiments)} experiments.")
except Exception as e:
    print(f"Failed to connect to MLflow: {e}")

from constants import Status

class ModelTrainingPipeline():
    def __init__(self, data, sample_dataset: bool=False, test_size: float=0.2 , random_number: int=42):
        self.X = None
        self.y = None
        self.data = data
        self.sample_dataset = sample_dataset

        self.status = "pending"
        self.progress = 0
        self.result = ''
        self.error = ''

        self.random_number = random_number
        self.test_size = test_size

        self.pipeline = None
    
    def data_preparation(self):
        self.X, self.y = self.data[:-1], self.data[-1]
        X_train, X_test, y_train, y_test = train_test_split(self.X, 
                                                            self.y,
                                                            test_size=self.test_size, 
                                                            random_state=self.random_number)
        return X_train, X_test, y_train, y_test

    def train_sample(self) -> None:
        try:
            self.status = Status.RUNNING.value

            iris = datasets.load_iris()
            self.X = iris.data
            self.y = iris.target 

            X_train, X_test, y_train, y_test = self.data_preparation()

            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=2)),
                ('classifier', LogisticRegression())
            ])

            mlflow.set_experiment("sample_training_pipeline")
            with mlflow.start_run() as run:
                self.pipeline.fit(X_train, y_train)
                y_pred = self.pipeline.predict(X_test)

                acc = self.metrics(y_pred, y_test)

                mlflow.log_metric("accuracy", acc)

                mlflow.sklearn.log_model(
                    sk_model=self.pipeline,
                    name="iris_pipeline_model",
                    registered_model_name="IrisPipelineModel"
                )

                self.result = {"accuracy": acc}
                self.status = Status.COMPLETED.value
                self.progress = 100

        except Exception as e:
            self.status = Status.FAILED.value
            self.error = f"An error occurred: {e}"
    
    def metrics(self, y_pred, y_test) -> float:
        acc = accuracy_score(y_pred, y_test)
        return acc
    
    def run(self) -> None:
        if self.sample_dataset:
            self.train_sample()
        else:
            pass
        
if __name__ == "__main__":
    pipeline = ModelTrainingPipeline(data=None, sample_dataset=True)
    pipeline.run()
    print("Status", pipeline.status)
    print("Result", pipeline.result)
    print("Error", pipeline.error)