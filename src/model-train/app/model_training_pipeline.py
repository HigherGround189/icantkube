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
from mlflow.models import infer_signature

import pandas as pd

from app.constants import Status, PipelineConfig, SAMPLE_CFG

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

class ModelTrainingPipeline():
    def __init__(self, 
                 update, 
                 mlflow_conn, 
                 trackingId: str, 
                 cfg: PipelineConfig,
                 *,
                 sample_dataset: bool=False, 
                 test_size: float=0.2 , 
                 random_number: int=42,
                 ):
        
        self.sample_dataset = sample_dataset
        self.update = update
        self.trackingId = trackingId.split(":")[-1]

        self.random_number = random_number
        self.test_size = test_size

        self.pipeline = None

        self.mlflow_enabled = mlflow_conn

        self.cfg = SAMPLE_CFG if sample_dataset else cfg

    
    def data_preparation(self, X, y):
        """
        Split dataset into train and test dataset
        
        X: pd.Dataframe
            Training features
        y: pd.Series
            Training labels
        """
        X_train, X_test, y_train, y_test = train_test_split(X, 
                                                            y,
                                                            test_size=self.test_size, 
                                                            random_state=self.random_number)
        return X_train, X_test, y_train, y_test

    def model_train_sample(self) -> None:
        """
        Sample of model training pipeline for initial testing
        using Iris dataset.

        Auto update the status and progress at each stage.
        """

        try:
            self.update(status=Status.RUNNING.value, progress=0)

            iris = datasets.load_iris() # Load iris dataset
            X = iris.data
            y = iris.target 

            self.update(progress=10)

            # Split into train and test dataset
            X_train, X_test, y_train, y_test = self.data_preparation(X, y)
            self.update(progress=30)

            # Create pipeline
            self.pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=2)),
                ('classifier', LogisticRegression())
            ])
            self.update(progress=50)
            
            # Start mlflow and set experiment
            run_context = nullcontext()
            if self.mlflow_enabled:
                # mlflow.set_experiment(self.cfg.experiment_name)
                # run_context = mlflow.start_run(f"{self.cfg.pipeline_name}-{self.trackingId}")
                mlflow.set_experiment("sample_training_pipeline")
                run_context = mlflow.start_run(run_name=f"iris-pipeline-{self.trackingId}")
            
            with run_context:
                self.pipeline.fit(X_train, y_train) # Train model
                self.update(progress=70)

                y_pred = self.pipeline.predict(X_test) # Predict output
                self.update(progress=80)

                acc = self.metrics(y_pred, y_test) # Calculate metrics
                self.update(progress=90)

                # Log into mlflow
                signature = infer_signature(X_test, y_pred)
                if self.mlflow_enabled:
                    mlflow.log_metric("accuracy", acc)
                    mlflow.sklearn.log_model(
                        sk_model=self.pipeline,
                        name=self.cfg.model_name,
                        registered_model_name=self.cfg.registered_model_name,
                        signature=signature
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
        """
        Actual model training pipeline to create model.

        Auto update the status and progress at each stage.
        """
        pass
    
    def metrics(self, y_pred, y_test) -> float:
        """
        Return model performance metrics
        
        Params:
            y_pred: pd.Series
                Model predicted label
            y_test: pd.Series
                Actual label

        Return:
            acc: float
                Measured accuracy result
        """
        acc = accuracy_score(y_pred, y_test)
        return acc
    
    def run(self) -> None:
        """
        Choice to run sample pipeline or actual training pipeline
        """
        if self.sample_dataset:
            self.model_train_sample()
        else:
            self.model_train()
        
# if __name__ == "__main__":
#     pipeline = ModelTrainingPipeline(data=None, sample_dataset=True)
#     pipeline.run()