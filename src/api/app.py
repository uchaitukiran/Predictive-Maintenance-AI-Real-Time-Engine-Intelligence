from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import sys
import os
import joblib
import re
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.insert(0, project_root)

# Import Components
from src.database.db import SessionLocal
from src.database.models import EngineSensorData, Prediction
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

# Define Paths Explicitly
WEBAPP_DIR = os.path.join(project_root, "webapp")

# ---------------------------------------------------------
# FLASK APP INITIALIZATION
# ---------------------------------------------------------
app = Flask(__name__, static_folder=WEBAPP_DIR) 
CORS(app)

# ---------------------------------------------------------
# CRITICAL FIX: DEFINE WEBPAGE ROUTES FIRST
# ---------------------------------------------------------

# 1. Serve Index.html (Root)
@app.route("/", methods=['GET'])
def index():
    try:
        index_path = os.path.join(WEBAPP_DIR, "index.html")
        return send_file(index_path)
    except Exception as e:
        return f"Error loading index.html: {e}", 404

# 2. Serve Static Files (Models, Textures, JS, CSS)
# This handles /models/engine.glb, /hdri/env.hdr, /js/viewer.js etc.
@app.route("/<path:filename>")
def serve_static_files(filename):
    try:
        file_path = os.path.join(WEBAPP_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

# ---------------------------------------------------------
# API SETUP (Happens AFTER webpage routes)
# ---------------------------------------------------------
api = Api(app, version='1.0', title='Engine Health Monitoring API',
          description='MNC Level API for Predictive Maintenance',
          doc='/docs')
ns = api.namespace('', description='Operations')

# ---------------------------------------------------------
# GLOBALS & MODEL LOADING
# ---------------------------------------------------------
current_simulation_id = 0

NLP_MODEL_PATH = os.path.join(project_root, "artifacts", "nlp_log_classifier.pkl")
nlp_model = None
try:
    nlp_model = joblib.load(NLP_MODEL_PATH)
    print("✅ NLP Model Loaded.")
except Exception as e:
    print(f"⚠️ NLP Error: {e}")

def clean_text_nlp(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

LSTM_MODEL_PATH = os.path.join(project_root, "artifacts", "lstm_model.keras")
SCALER_PATH = os.path.join(project_root, "artifacts", "lstm_scaler.pkl")
Y_SCALER_PATH = os.path.join(project_root, "artifacts", "lstm_y_scaler.pkl")

lstm_model = None
lstm_scaler = None
y_scaler = None
SEQUENCE_LENGTH = 30
history_buffer = deque(maxlen=SEQUENCE_LENGTH)

FEATURE_ORDER = [
    'op_setting_1', 'op_setting_2', 'op_setting_3',
    'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9',
    'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 
    'sensor_17', 'sensor_20', 'sensor_21'
]

try:
    lstm_model = load_model(LSTM_MODEL_PATH)
    lstm_scaler = joblib.load(SCALER_PATH)
    y_scaler = joblib.load(Y_SCALER_PATH)
    print("✅ LSTM Model & Scalers Loaded.")
except Exception as e:
    print(f"⚠️ LSTM Error: {e}")

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.route("/reset", methods=['GET'])
def reset_simulation():
    global current_simulation_id
    current_simulation_id = 0
    return jsonify({'status': 'reset', 'message': 'Simulation restarted'})

@app.route("/get_real_data", methods=['GET'])
def get_real_data():
    global current_simulation_id
    db = SessionLocal()
    try:
        current_simulation_id += 1
        row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()
        if not row:
            current_simulation_id = 1
            row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()

        if row:
            return jsonify({
                'id': row.id,
                'op_setting_1': row.op_setting_1, 'op_setting_2': row.op_setting_2, 'op_setting_3': row.op_setting_3,
                'sensor_2': row.sensor_2, 'sensor_3': row.sensor_3, 'sensor_4': row.sensor_4,
                'sensor_7': row.sensor_7, 'sensor_8': row.sensor_8, 'sensor_9': row.sensor_9,
                'sensor_11': row.sensor_11, 'sensor_12': row.sensor_12, 'sensor_13': row.sensor_13,
                'sensor_14': row.sensor_14, 'sensor_15': row.sensor_15, 'sensor_17': row.sensor_17,
                'sensor_20': row.sensor_20, 'sensor_21': row.sensor_21
            })
        else:
            return jsonify({'error': 'Database is empty'})
    finally:
        db.close()

@ns.route('/predict')
class PredictResource(Resource):
    def post(self):
        db = SessionLocal()
        try:
            data = request.get_json()
            custom_data = CustomData(
                op_setting_1=float(data.get('op_setting_1', 0)), op_setting_2=float(data.get('op_setting_2', 0)), op_setting_3=float(data.get('op_setting_3', 0)),
                sensor_2=float(data.get('sensor_2', 0)), sensor_3=float(data.get('sensor_3', 0)), sensor_4=float(data.get('sensor_4', 0)),
                sensor_7=float(data.get('sensor_7', 0)), sensor_8=float(data.get('sensor_8', 0)), sensor_9=float(data.get('sensor_9', 0)),
                sensor_11=float(data.get('sensor_11', 0)), sensor_12=float(data.get('sensor_12', 0)), sensor_13=float(data.get('sensor_13', 0)),
                sensor_14=float(data.get('sensor_14', 0)), sensor_15=float(data.get('sensor_15', 0)), sensor_17=float(data.get('sensor_17', 0)),
                sensor_20=float(data.get('sensor_20', 0)), sensor_21=float(data.get('sensor_21', 0))
            )
            pred_df = custom_data.get_data_as_data_frame()
            predict_pipeline = PredictPipeline()
            results = predict_pipeline.predict(pred_df)
            rul_value = float(results[0])

            if rul_value > 100: state = "GOOD"
            elif rul_value > 30: state = "WARNING"
            else: state = "CRITICAL"

            new_pred = Prediction(state=state, rul=rul_value, temperature=data.get('sensor_2', 0), pressure=data.get('sensor_7', 0), vibration=data.get('sensor_4', 0))
            db.add(new_pred)
            db.commit()
            return {'Predicted_RUL': rul_value, 'state': state}

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {'error': str(e)}, 500
        finally:
            db.close()

@app.route("/analyze_log", methods=["POST"])
def analyze_log():
    if not nlp_model: return jsonify({"error": "NLP Model not loaded"}), 500
    data = request.get_json()
    log_message = data.get("log_message", "")
    state = data.get("state", "NORMAL")
    if not log_message:
        if state == "WARNING": log_message = "High vibration detected in compressor section."
        elif state == "CRITICAL": log_message = "Critical failure detected in turbine blades!"
        else: log_message = "All systems operational."
    clean_msg = clean_text_nlp(log_message)
    prediction = nlp_model.predict([clean_msg])[0]
    return jsonify({"log_message": log_message, "predicted_status": prediction})

@app.route("/predict_lstm", methods=["POST"])
def predict_lstm():
    if not lstm_model or not lstm_scaler or not y_scaler:
        return jsonify({"error": "LSTM Model not loaded", "prediction": 0, "status": "ERROR"}), 500
    try:
        data = request.get_json()
        input_list = []
        for col in FEATURE_ORDER:
            val = data.get(col, 0)
            if val is None: val = 0
            input_list.append(float(val))
        input_data = np.array([input_list])
        scaled_data = lstm_scaler.transform(input_data)
        history_buffer.append(scaled_data[0])
        if len(history_buffer) < SEQUENCE_LENGTH:
            return jsonify({"prediction": 0, "status": "ACCUMULATING", "message": f"Collecting cycle {len(history_buffer)}/{SEQUENCE_LENGTH}..."})
        sequence = np.array([list(history_buffer)])
        prediction_scaled = lstm_model.predict(sequence, verbose=0)
        rul_real = y_scaler.inverse_transform(prediction_scaled)[0][0]
        rul_real = max(0, rul_real) 
        return jsonify({"prediction": float(rul_real), "status": "ACTIVE", "message": "Deep Learning Analysis Complete"})
    except Exception as e:
        print(f"❌ LSTM Error: {e}")
        return jsonify({"error": str(e), "prediction": 0, "status": "ERROR"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)