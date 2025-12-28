from flask import Flask, jsonify, request, render_template
from io import BytesIO
from enum import Enum
import pandas as pd

app = Flask(__name__)

jobCounter = 1
stateTracker = {}

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@app.get("/health")
def health():
    return {"status": "running"}

@app.route("/")
def index():    # Temporary
    """Testing file upload locally"""
    return render_template("index.html")

def retrieve_id(trackingId: int):
    return stateTracker.get(trackingId, None)

def model_training():
    pass

@app.route('/start', methods=["POST"])
def start_training():
    global jobCounter
    file = request.files.get('filename', None)
    if file in [None, '']:
        return jsonify({'error':'File not provided'}), 400
    
    trackingId = jobCounter
    jobCounter += 1
    stateTracker[trackingId] = {'status':Status.PENDING.value, 'progress':0, 'result':None, 'error':None}   

    data = file.read()
    if not data:
        stateTracker[trackingId]['status'] = Status.FAILED.value
        stateTracker[trackingId]['error'] = 'File is empty'
        return jsonify({'trackingId':trackingId})
    
    try:
        df = pd.read_csv(BytesIO(data))
    except Exception as e:
        stateTracker[trackingId]['status'] = Status.FAILED.value
        stateTracker[trackingId]['error'] = f'Failed to read CSV: {e}'
        return jsonify({'trackingId':trackingId})
    
    return jsonify({'trackingId':trackingId})

@app.route('/status', methods=["GET"])
def retrieve_all_status():
    return jsonify({'trackingID':stateTracker})

@app.route('/status/<int:trackingId>', methods=["GET"])
def retrieve_id_status(trackingId: int):
    job = retrieve_id(trackingId)
    if job is None:
        return jsonify({'error': f'Tracking ID ({trackingId}) does not exist'}), 404
    return jsonify(job)

if __name__=="__main__":
    app.run(port=80)