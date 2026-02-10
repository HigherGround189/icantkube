from celery import Celery
from app.model_training_pipeline import ModelTrainingPipeline
from app.connections import (
    connect_redis, 
    connect_mlflow,
    connect_rustfs, 
    connect_mariadb
    )
from app.constants import PipelineConfig
from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

import pandas as pd
from time import sleep

from app.config import load_apps

APPS = load_apps()

r = connect_redis(0)

r1 = connect_redis(1)
host = r1.connection_pool.connection_kwargs['host']
port = r1.connection_pool.connection_kwargs['port']

app = Celery('tasks', broker=f'redis://{host}:{port}/1')
mlfow = connect_mlflow()
rustfs = connect_rustfs()
mariadb = connect_mariadb()

table_name = APPS["mariadb-connection"]["table"]

@app.task(bind=True)
def start_model_training(self, object_key: str, machine_name: str, trackingId: str):
    """
    Initiate model training pipeline
    
    Params:
        trackingId: str
            Retrieved job tracking ID to monitor the status
    """
    def state_update(**kwargs):
        """
        Update job status
        
        Params:
            **kwargs: JSON: {
                    'status': str       # pending | running | completed | failed
                    'progress': int,    # 0-100
                    'result': str,
                    'error': str
                    }
                Retrieve real time update for specified key
        """
        # Update in redis
        r.hset(trackingId, mapping=kwargs)

        # Update in mariadb
        field_map = {
            "status": "status",
            "progress": "training_progress",
        }
        fields = []
        values = []

        for key, value in kwargs.items():
            if key in field_map:
                fields.append(f"{key} = %s")
                values.append(value)
        
        query = f"""
                UPDATE {table_name}
                SET {', '.join(fields)}
                WHERE machine = {machine_name}
                """

        cursor = mariadb.cursor()
        cursor.execute(query, values)
        mariadb.commit()
    
    CFG = PipelineConfig(
        experiment_name=machine_name,
        pipeline_name=machine_name,
        model_name=machine_name,
        registered_model_name=machine_name,
    )

    logger.info("Initiating Model Training...")
    pipeline = ModelTrainingPipeline(
                                    #  sample_dataset=True, 
                                     update=state_update, 
                                     mlflow_conn=mlfow,
                                     rustfs_conn=rustfs,
                                     object_key=object_key,
                                     trackingId=trackingId, 
                                     cfg=CFG,
                                     )
    pipeline.run()