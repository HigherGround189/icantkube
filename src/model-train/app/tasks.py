from celery import Celery
from app.model_training_pipeline import ModelTrainingPipeline
from app.connections import connect_redis
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

@app.task()
def start_model_training(data, trackingId):
    def state_update(**kwargs):
        r.hset(trackingId, mapping=kwargs)

    logger.info("Initiating Model Training...")
    pipeline = ModelTrainingPipeline(data=data, sample_dataset=True, update=state_update)
    pipeline.run()
