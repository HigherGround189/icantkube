from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from contextlib import nullcontext
import os
import mlflow

from app.constants import Status

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

os.environ['MLFLOW_TRACKING_USERNAME'] = os.environ.get("username")
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.environ.get("password")

def connect_mlflow():
    candidates = [
        {"host": "https://mlflow.icantkube.help"},
        {"host": "http://localhost:5200"} # local testing
    ]
    for i, uri in enumerate(candidates):
        try:
            mlflow.set_tracking_uri(uri["host"])
            experiments = mlflow.search_experiments(max_results=1)
            if experiments:
                logger.info(f"Connected to MLflow Succefully!")
                return True
        except Exception as e:
            logger.warning(f"Failed to connect to MLflow: {uri["host"]}: {e}")
            if i < len(candidates) - 1:
                logger.info("Trying next MLFlow candidate...")

    logger.warning("MLflow unavailable, continuing without tracking")
    return False

class ModelTrainingPipeline():
    def __init__(self, data, sample_dataset: bool=False, test_size: float=0.2 , random_number: int=42):
        self.data = True if data else False
        self.sample_dataset = sample_dataset

        self.status = Status.PENDING.value
        self.progress = 0
        self.result = ''
        self.error = ''

        self.random_number = random_number
        self.test_size = test_size

        self.pipeline = None

        self.mlflow_enabled = connect_mlflow()

    
    def data_preparation(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, 
                                                            y,
                                                            test_size=self.test_size, 
                                                            random_state=self.random_number)
        return X_train, X_test, y_train, y_test

    def model_train_sample(self) -> None:
        try:
            self.status = Status.RUNNING.value

            iris = datasets.load_iris()
            X = iris.data
            y = iris.target 

            X_train, X_test, y_train, y_test = self.data_preparation(X, y)

            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=2)),
                ('classifier', LogisticRegression())
            ])

            run_context = nullcontext()

            if self.mlflow_enabled:
                mlflow.set_experiment("sample_training_pipeline")
                run_context = mlflow.start_run()
            
            with run_context:
                self.pipeline.fit(X_train, y_train)
                y_pred = self.pipeline.predict(X_test)

                acc = self.metrics(y_pred, y_test)

                if self.mlflow_enabled:
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
    
    def model_train():
        pass
    
    def metrics(self, y_pred, y_test) -> float:
        acc = accuracy_score(y_pred, y_test)
        return acc
    
    def run(self) -> None:
        if self.sample_dataset:
            self.model_train_sample()
        else:
            self.model_train()
        
if __name__ == "__main__":
    pipeline = ModelTrainingPipeline(data=None, sample_dataset=True)
    pipeline.run()
    print("Status", pipeline.status)
    print("Result", pipeline.result)
    print("Error", pipeline.error)