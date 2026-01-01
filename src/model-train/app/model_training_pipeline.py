from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from contextlib import nullcontext
import json
import os
import mlflow

import pandas as pd

from app.constants import Status

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

from app.connections import connect_mlflow

class ModelTrainingPipeline():
    def __init__(self, update, data, sample_dataset: bool=False, test_size: float=0.2 , random_number: int=42):
        self.data = True if data else False
        self.sample_dataset = sample_dataset
        self.update = update

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
            self.update(status=Status.RUNNING.value, progress=0)

            iris = datasets.load_iris()
            X = iris.data
            y = iris.target 

            self.update(progress=10)

            X_train, X_test, y_train, y_test = self.data_preparation(X, y)
            self.update(progress=30)

            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=2)),
                ('classifier', LogisticRegression())
            ])
            self.update(progress=50)

            run_context = nullcontext()

            if self.mlflow_enabled:
                mlflow.set_experiment("sample_training_pipeline")
                run_context = mlflow.start_run()
            
            with run_context:
                self.pipeline.fit(X_train, y_train)
                self.update(progress=70)

                y_pred = self.pipeline.predict(X_test)
                self.update(progress=80)

                acc = self.metrics(y_pred, y_test)
                self.update(progress=90)

                if self.mlflow_enabled:
                    mlflow.log_metric("accuracy", acc)
                    mlflow.sklearn.log_model(
                        sk_model=self.pipeline,
                        name="iris_pipeline_model",
                        registered_model_name="IrisPipelineModel"
                    )

                self.update(status=Status.COMPLETED.value, 
                            progress=100, 
                            result=json.dumps({"accuracy": acc})
                            )

        except Exception as e:
            self.update(status=Status.FAILED.value, 
                        error=f"An error occurred: {e}"
                        )
    
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