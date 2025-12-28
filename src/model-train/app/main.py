from flask import Flask, jsonify, request, render_template
from io import BytesIO
from enum import Enum
import pandas as pd

app = Flask(__name__)

counter = 0

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.route("/")
def index():    # Temporary
    """Testing file upload locally"""
    return render_template("index.html")

@app.route('/start', methods=["POST"])
def start_training():
    file = request.files.get('filename', None)
    if file in [None, '']:
        return jsonify({'status':Status.FAILED.value, 'error':'file not detected'}), 400
    
    data = file.read()
    if data:
        df = pd.read_csv(BytesIO(data))
        df_json = df.to_json(orient='records')
        return jsonify({"data": df_json})
    else:
        return jsonify({'status':Status.FAILED.value, 'error':'Issue reading file'}), 400
    # return jsonify({'trackingId':1})

@app.route('/status/<int:trackingId>', methods=["GET"])
def retrieve_status(trackingId: int):
    global counter
    counter += 1
    if counter % 5 == 0:
        return jsonify({'status':'completed', 'result':{'accuracy':100}})
    return jsonify({'status':'running', 'progress':counter%5*20})

if __name__=="__main__":
    app.run(port=80)