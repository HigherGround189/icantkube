from flask import Flask, jsonify, request, render_template
from io import BytesIO
from enum import Enum
import pandas as pd

app = Flask(__name__)

counter = 0
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

@app.route('/start', methods=["POST"])
def start_training():
    global jobCounter
    file = request.files.get('filename', None)
    trackingId = jobCounter
    jobCounter += 1

    stateTracker[trackingId] = {'status':Status.PENDING.value, 'progress':0, 'result':None, 'error':None}    

    if file in [None, '']:
        stateTracker[trackingId]['status'] = Status.FAILED.value
        stateTracker[trackingId]['error'] = 'File not detected'
        return jsonify({'trackingId':trackingId})
    
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
    
    stateTracker[trackingId]['progress'] = 100
    return jsonify({'trackingId':trackingId})

@app.route('/status', methods=["GET"])
def retrieve_all_status():
    return jsonify({'trackingID':stateTracker})

@app.route('/status/<int:trackingId>', methods=["GET"])
def retrieve_id_status(trackingId: int):
    global counter
    counter += 1
    if counter % 5 == 0:
        return jsonify({'status':'completed', 'result':{'accuracy':100}})
    return jsonify({'status':'running', 'progress':counter%5*20})

if __name__=="__main__":
    app.run(port=80)