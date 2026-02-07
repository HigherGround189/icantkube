from flask import Flask, jsonify, request, render_template
from io import BytesIO
import requests
from datetime import datetime, timezone
import pandas as pd
import redis
import json
from typing import Optional
import uuid
from botocore.exceptions import ClientError

from app.tasks import start_model_training

from app.constants import Status

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

from app.config import load_apps

APPS = load_apps()

from app.connections import (
    connect_redis, 
    connect_rustfs, 
    create_or_connect_bucket
    )
r = connect_redis(db=0)
rustfs = connect_rustfs()
bucket_name = APPS["rustfs-connection"]["bucket"]

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "running"})

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

def save_dataset(raw_bytes, contentType, filename: str, jobId: str, ) -> str:
    """
    Docstring for save_dataset
    
    Params:
        raw_bytes:
            File uploaded
        contentType: str
            Content type of file
        filename: str
            Machine name to be name on file
        jobId: str
            trackingId to be assigned to object key
    
    Returns:
        key: str
            object key to use to retrieve uploaded data
    """
    try:
        id = jobId.removeprefix("job:")
        key = f"{id}.csv"
        size = str(len(raw_bytes))
        if size == 0:
            return jsonify({"error": "Uploaded data has 0 bytes"}), 400

        create_or_connect_bucket(rustfs, bucket_name=bucket_name)

        metadata = {
            "Metadata":{
            "jobId":jobId,
            "filename": filename,
            "size": size,
            "uploadedAt": datetime.now(timezone.utc),
            },
        }

        url = rustfs.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                "Bucket":bucket_name,
                "Key":key,
                "ContentType":contentType,
                "Metadata":metadata,
            },
            ExpiresIn=300,
        )

        requests.put(
            url,
            headers={"ContentType": contentType},
            data=raw_bytes
        )
        # Body=BytesIO(raw_bytes)

        logger.info(f"Upload {key} to storage successfully")
        return key
    except ClientError as e:
        logger.error(f"Error uploading {key}: {e}")
        return jsonify({'error':f'Failed to upload {key}'}), 500
        

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

    raw_bytes = request.get_data(parse_form_data=True)
    content_type = request.content_type
    machine_name = request.args.get('name')

    if not raw_bytes:
        return jsonify({"error": "Missing data body"}), 400
    
    if not machine_name:
        return jsonify({"error": "Missing `name` parameter"}), 400
    
    return_id = uuid.uuid4()
    trackingId = f'job:{return_id}'
    newIdInstance = {'status':Status.PENDING.value, 'progress':0, 'result':'', 'error':''}
    r.hset(trackingId, mapping=newIdInstance)

    logger.info("Retrieving Content...")
    
    try:
        # df = pd.read_csv(BytesIO(raw_bytes))
        object_key = save_dataset(raw_bytes, contentType=content_type, filename=machine_name, jobId=trackingId)
        task = start_model_training.delay(object_key, machine_name, trackingId)
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