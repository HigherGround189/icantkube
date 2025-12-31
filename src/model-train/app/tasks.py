from celery import Celery
from model_training_pipeline import ModelTrainingPipeline
import pandas as pd
from time import sleep

# app = Celery('tasks', broker='redis-master.redis.svc.cluster.local/0', backend='redis-master.redis.svc.cluster.local/1')
app = Celery('tasks', broker='redis://localhost:6370/0', backend='redis://localhost:6370/1')

@app.task()
def start_model_training(data):
    pipeline = ModelTrainingPipeline(data=data)
    pipeline.run()
    return pipeline.status
