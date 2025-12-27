from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/start', methods=["POST"])
def start_training():
    return jsonify({"action":'initiate training...'})

@app.route('/status/<trackingId>', methods=["GET"])
def retrieve_status(trackingId):
    return jsonify({'status':'completed'})

if __name__=="__main__":
    app.run(port=80)