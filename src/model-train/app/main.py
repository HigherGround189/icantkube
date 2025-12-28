from flask import Flask, jsonify, request
from io import BytesIO
from enum import Enum

app = Flask(__name__)

counter = 0

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@app.route('/start', methods=["POST"])
def start_training():
    return jsonify({'trackingId':1})

@app.route('/status/<int:trackingId>', methods=["GET"])
def retrieve_status(trackingId: int):
    global counter
    counter += 1
    if counter % 5 == 0:
        return jsonify({'status':'completed', 'result':{'accuracy':100}})
    return jsonify({'status':'running', 'progress':counter%5*20})

if __name__=="__main__":
    app.run(port=80)