from flask import Flask, jsonify, request, render_template
from io import BytesIO
import pandas as pd
import redis
import json
from typing import Optional
import uuid

from app.tasks import start_model_training

from app.constants import Status

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

from app.connections import connect_redis
r = connect_redis(db=0)

app = Flask(__name__)

# jobCounter = 1
# stateTracker = {}

@app.get("/health")
def health():
    return {"status": "running"}

@app.route("/")
def index():    # Temporary
    """Testing file upload locally"""
    return render_template("index.html")

def retrieve_id(trackingId: str) -> Optional[dict]:
    """ 
    Retrieve job state based on specified trackingId.
    
    Returns:
        dict: Job data if trackingId exist
        None: If job does not exist
    """
    job = r.hgetall(f'job:{trackingId}')
    if not job:
        return None
    return job

@app.route('/start', methods=["POST"])
def job_initiation():
    """
    Process uploaded file, assign and create a new training job.

    Returns:
        Json: {
            trackingId: str
        }
    """
    logger.info("Reading uploaded file...")
    file = request.files.get('filename', None)
    if file in [None, '']:
        return jsonify({'error':'File not provided'}), 400
    
    return_id = uuid.uuid4()
    trackingId = f'job:{return_id}'
    newIdInstance = {'status':Status.PENDING.value, 'progress':0, 'result':'', 'error':''}
    r.hset(trackingId, mapping=newIdInstance)

    logger.info("Retrieving Content...")
    data = file.read()
    if not data:
        r.hset(trackingId, 'status', Status.FAILED.value)
        r.hset(trackingId, 'error', 'File is empty')
        return jsonify({'trackingId':return_id})
    
    try:
        df = pd.read_csv(BytesIO(data))
        df_json = df.to_json(orient='records')
        task = start_model_training.delay(df_json, trackingId)
        logger.info(f"Task: {task}")
        logger.info(f"Registered trackingId: {trackingId}")

    except Exception as e:
        r.hset(trackingId, 'status', Status.FAILED.value)
        r.hset(trackingId, 'error', f'Failed to read CSV: {e}')
        return jsonify({'trackingId':return_id})
    
    return jsonify({'trackingId':return_id})

@app.route('/status', methods=["GET"])
def retrieve_all_status():
    """
    Retrieve all available jobs and their status.

    Return:
        JSON: {
            'trackingId': str
            'status': str   # pending | running | completed | failed
        }
    """
    jobs = []
    for key in r.scan_iter('job:*'):
        trackingId = str(key.split(":")[1])
        status = r.hget(key, 'status')
        jobs.append({'trackingId':trackingId, 'status':status})
    return jsonify(jobs)

@app.route('/status/<trackingId>', methods=["GET"])
def retrieve_id_status(trackingId: str):
    """
    Retrieve the current state of job.

    Parameters:
        trackingId: str
            Unique ID of the job to check

    Return:
        JSON: {
            'status': str,      # pending | running | completed | failed
            'progress': int,    # 0-100
            'result': str,
            'error': str
        }
    """
    job = retrieve_id(trackingId)
    if job is None:
        return jsonify({'error': f'Tracking ID ({trackingId}) does not exist'}), 404
    return jsonify(job)

if __name__=="__main__":
    app.run(port=80)