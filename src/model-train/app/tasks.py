from celery import Celery
from app.model_training_pipeline import ModelTrainingPipeline
from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

import pandas as pd
from time import sleep

# app = Celery('tasks', broker='redis-master.redis.svc.cluster.local/0', backend='redis-master.redis.svc.cluster.local/1')
app = Celery('tasks', broker='redis://localhost:6370/1', backend='redis://localhost:6370/2')

@app.task()
def start_model_training(data):
    logger.info("Initiating Model Training...")
    pipeline = ModelTrainingPipeline(data=data, sample_dataset=True)
    pipeline.run()
    return f'Status: {pipeline.status}, Data Received: {pipeline.data}'
