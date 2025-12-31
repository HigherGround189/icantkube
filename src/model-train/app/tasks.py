from celery import Celery
from model_training_pipeline import ModelTrainingPipeline
from time import sleep

# app = Celery('tasks', broker='redis-master.redis.svc.cluster.local/0', backend='redis-master.redis.svc.cluster.local/1')
app = Celery('tasks', broker='redis://localhost:6370/0', backend='redis://localhost:6370/1')

@app.task()
def add(x, y):
    i = 0
    while i < 100:
        sleep(1)
        i += 1
        print("testing...")
    return x + y
