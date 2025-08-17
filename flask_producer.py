from flask import Flask, jsonify
from kafka import KafkaProducer
import json
import random
from datetime import datetime
import hashlib

app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_vitals():
    hadm_id = random.randint(1000, 9999)
    hashed_id = hashlib.sha256(str(hadm_id).encode()).hexdigest()
    return {
        "hadm_id": hashed_id,
        "HR": random.randint(60, 120),
        "TEMP": round(random.uniform(97.0, 103.0), 1),
        "SPO2": random.randint(90, 100),
        "masktype": random.choice([0, 1]),
        "timestamp": datetime.now().isoformat()
    }

@app.route('/')
def health_check():
    return jsonify({"status": "Producer is running", "endpoints": ["/send-vitals"]})

@app.route('/send-vitals', methods=['GET'])
def send_vitals():
    try:
        vitals = generate_vitals()
        producer.send('patient_vitals', vitals)
        producer.flush()  # Ensure message is sent
        return jsonify({"status": "success", "message": "Vitals sent", "data": vitals})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)