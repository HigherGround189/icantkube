from celery import Celery
from app.model_training_pipeline import ModelTrainingPipeline
from app.connections import connect_redis, connect_mlflow
from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

import pandas as pd
from time import sleep

r = connect_redis(0)

r1 = connect_redis(1)
host = r1.connection_pool.connection_kwargs['host']
port = r1.connection_pool.connection_kwargs['port']

app = Celery('tasks', broker=f'redis://{host}:{port}/1')
mlfow = connect_mlflow()

@app.task(bind=True)
def start_model_training(self, data, trackingId):
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
        r.hset(trackingId, mapping=kwargs)

    logger.info("Initiating Model Training...")
    pipeline = ModelTrainingPipeline(data=data, sample_dataset=True, update=state_update, mlflow_conn=mlfow)
    pipeline.run()