from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from contextlib import nullcontext
from functools import wraps
from typing import Tuple
import json
import os
from io import BytesIO

import mlflow
from mlflow.models import infer_signature
from mlflow.data.pandas_dataset import from_pandas

from botocore.exceptions import ClientError

import pandas as pd

from app.constants import Status, PipelineConfig, SAMPLE_CFG

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

from app.config import load_apps

APPS = load_apps()

def training_template(func):
    """
    Training skeleton to replicate the procedure from loading data to model training and 
    evaluation to logging metrics and artifacts
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self.update(status=Status.RUNNING.value, progress=0)

            df, X, y, _ = func(self, *args, **kwargs) # Retrieve Features and label
            self.update(progress=10)

            # Split into train and test dataset
            X_train, X_test, y_train, y_test = self.data_preparation(X, y)
            self.update(progress=30)

            # Retrieve pipeline
            _, _, _, pipeline = func(self, *args, **kwargs)
            self.update(progress=50)
            
            # Start mlflow and set experiment
            run_context = nullcontext()
            if self.mlflow_enabled:
                mlflow.set_experiment(self.cfg.experiment_name)
                run_context = mlflow.start_run(f"{self.cfg.pipeline_name}-{self.trackingId}")
            
            with run_context:
                pipeline.fit(X_train, y_train) # Train model
                self.update(progress=70)

                y_pred = pipeline.predict(X_test) # Predict output
                self.update(progress=80)

                acc = self.metrics(y_pred, y_test) # Calculate metrics
                self.update(progress=90)

                # Log into mlflow
                signature = infer_signature(X_test, y_pred)
                if self.mlflow_enabled:
                    mlflow.log_metric("accuracy", acc)
                    mlflow.sklearn.log_model(
                        sk_model=pipeline,
                        name=self.cfg.model_name,
                        registered_model_name=self.cfg.registered_model_name,
                        signature=signature
                    )
                    if self.sample_dataset:
                        dataset = from_pandas(
                                df,
                                source="sklearn.datasets.load_iris()",
                                name="iris_sample_dataset",
                            )
                    else:
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_bytes = csv_buffer.getvalue()
                        mlflow.log_bytes(csv_bytes, f"{self.cfg.model_name}.csv", artifact_path="datasets")
                        dataset = from_pandas(df)
                    
                    mlflow.log_input(dataset, context="training")
                    self.rustfs_enabled.delete_object(Bucket=self.bucket_name, Key=self.object_key)

                self.update(status=Status.COMPLETED.value, 
                            progress=100, 
                            result=json.dumps({"accuracy": acc})
                            )

        except Exception as e:
            self.update(status=Status.FAILED.value, 
                        error=f"An error occurred: {e}"
                        )
    return wrapper

class ModelTrainingPipeline():
    def __init__(self, 
                 update, 
                 mlflow_conn, 
                 rustfs_conn,
                 object_key: str,
                 trackingId: str, 
                 cfg: PipelineConfig,
                 *,
                 sample_dataset: bool=False, 
                 test_size: float=0.2 , 
                 random_number: int=42,
                 ):
        
        self.sample_dataset = sample_dataset
        self.update = update
        self.trackingId = trackingId.removeprefix("job:")

        self.object_key = object_key
        self.bucket_name = APPS["rustfs-connection"]["bucket"]

        self.random_number = random_number
        self.test_size = test_size

        self.rustfs_enabled = rustfs_conn
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
    
    def retrieve_data(self) -> Tuple[BytesIO, pd.DataFrame]:
        """
        Retrieve the dataset to be used to train a model
        
        Return:
            df: pd.DataFrame
                Return the retrieved dataset
        """
        try:
            client = self.rustfs_enabled.get_object(Bucket=self.bucket_name, Key=self.object_key)
            data_bytes = client["Body"].read()

            if not data_bytes:
                self.update(status=Status.FAILED.value, 
                        error=f"An error occurred: Object is empty: s3://{self.bucket_name}/{self.object_key}"
                        )

            bio = BytesIO(data_bytes)
            df = pd.read_csv(bio)
            return df

        except ClientError as e:
            self.update(status=Status.FAILED.value, 
                        error=f"An error occurred: Failed to download object {self.bucket_name}/{self.object_key}\n{e}"
                        )

    @training_template
    def model_train_sample(self) -> Tuple[pd.DataFrame, pd.Series, Pipeline]:
        """
        Sample of model training pipeline for initial testing
        using Iris dataset.

        Auto update the status and progress at each stage.
        """
        iris = datasets.load_iris() # Load iris dataset
        X = iris.data
        y = iris.target 

        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=2)),
            ('classifier', LogisticRegression())
        ])

        return iris, X, y, pipeline
            
    @training_template
    def model_train(self) -> Tuple[pd.DataFrame, pd.Series, Pipeline]:
        """
        Actual model training pipeline to create model.

        Auto update the status and progress at each stage.
        """
        df = self.retrieve_data() # Load uploaded dataset
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
         # Create pipeline
        pipeline = Pipeline([
            # Code
            # ...
        ])
        return df, X, y, pipeline
    
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