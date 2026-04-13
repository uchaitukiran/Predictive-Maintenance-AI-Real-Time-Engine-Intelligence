from flask import Flask, request, jsonify, send_file, send_from_directory
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
from src.database.models import EngineSensorData, Prediction, MaintenanceReport
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

# Safe Import for Reports
try:
    from src.utils.report_generator import generate_maintenance_report, create_pdf_file
    print("✅ Report Generator Ready.")
except Exception as e:
    print(f"⚠️ Report Generator Disabled: {e}")
    generate_maintenance_report = None
    create_pdf_file = None

# Define Paths
WEBAPP_DIR = os.path.join(project_root, "webapp")

# Initialize Flask
app = Flask(__name__, static_folder=WEBAPP_DIR) 
CORS(app)

# Routes for Webpage
@app.route("/", methods=['GET'])
def index():
    try:
        index_path = os.path.join(WEBAPP_DIR, "index.html")
        return send_file(index_path)
    except Exception as e:
        return f"Error loading index.html: {e}", 404

@app.route("/<path:path>")
def serve_static(path):
    try:
        file_path = os.path.join(WEBAPP_DIR, path)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

# API Setup
api = Api(app, version='1.0', title='Engine Health Monitoring API', doc='/docs')
ns = api.namespace('', description='Operations')

# Global Variables
current_simulation_id = 0

# Model Loading
NLP_MODEL_PATH = os.path.join(project_root, "artifacts", "nlp_log_classifier.pkl")
nlp_model = joblib.load(NLP_MODEL_PATH) if os.path.exists(NLP_MODEL_PATH) else None
if nlp_model: print("✅ NLP Model Loaded.")

def clean_text_nlp(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# LSTM Loading
LSTM_MODEL_PATH = os.path.join(project_root, "artifacts", "lstm_model.keras")
SCALER_PATH = os.path.join(project_root, "artifacts", "lstm_scaler.pkl")
Y_SCALER_PATH = os.path.join(project_root, "artifacts", "lstm_y_scaler.pkl")

lstm_model = load_model(LSTM_MODEL_PATH) if os.path.exists(LSTM_MODEL_PATH) else None
lstm_scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
y_scaler = joblib.load(Y_SCALER_PATH) if os.path.exists(Y_SCALER_PATH) else None
if lstm_model: print("✅ LSTM Model Loaded.")

SEQUENCE_LENGTH = 30
history_buffer = deque(maxlen=SEQUENCE_LENGTH)
FEATURE_ORDER = ['op_setting_1', 'op_setting_2', 'op_setting_3', 'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 'sensor_17', 'sensor_20', 'sensor_21']

# API Endpoints
@app.route("/reset", methods=['GET'])
def reset_simulation():
    global current_simulation_id
    current_simulation_id = 0
    return jsonify({'status': 'reset'})

@app.route("/get_real_data", methods=['GET'])
def get_real_data():
    global current_simulation_id
    db = SessionLocal()
    try:
        current_simulation_id += 1
        row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()
        
        # If we reached the end of data, loop back to 1
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
            # This handles the case where the database is completely empty
            return jsonify({'error': 'Database is empty'}), 404
            
    except Exception as e:
        print(f"❌ Error in get_real_data: {e}")
        return jsonify({'error': str(e)}), 500
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
            state = "GOOD" if rul_value > 100 else "WARNING" if rul_value > 30 else "CRITICAL"
            new_pred = Prediction(state=state, rul=rul_value, temperature=data.get('sensor_2', 0), pressure=data.get('sensor_7', 0), vibration=data.get('sensor_4', 0))
            db.add(new_pred)
            db.commit()
            return {'Predicted_RUL': rul_value, 'state': state}
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            db.close()

@app.route("/analyze_log", methods=["POST"])
def analyze_log():
    if not nlp_model: return jsonify({"error": "NLP Model not loaded"}), 500
    data = request.get_json()
    state = data.get("state", "NORMAL")
    log_message = data.get("log_message", "")
    if not log_message:
        if state == "WARNING": log_message = "High vibration in compressor."
        elif state == "CRITICAL": log_message = "Fire detected!"
        else: log_message = "All systems operational."
    clean_msg = clean_text_nlp(log_message)
    prediction = nlp_model.predict([clean_msg])[0]
    return jsonify({"log_message": log_message, "predicted_status": prediction})

@app.route("/predict_lstm", methods=["POST"])
def predict_lstm():
    if not lstm_model or not lstm_scaler or not y_scaler: return jsonify({"error": "LSTM not loaded"}), 500
    try:
        data = request.get_json()
        input_list = [float(data.get(col, 0)) for col in FEATURE_ORDER]
        input_data = np.array([input_list])
        scaled_data = lstm_scaler.transform(input_data)
        history_buffer.append(scaled_data[0])
        if len(history_buffer) < SEQUENCE_LENGTH:
            return jsonify({"prediction": 0, "status": "ACCUMULATING", "message": f"Cycle {len(history_buffer)}/{SEQUENCE_LENGTH}"})
        sequence = np.array([list(history_buffer)])
        pred_scaled = lstm_model.predict(sequence, verbose=0)
        rul = max(0, y_scaler.inverse_transform(pred_scaled)[0][0])
        return jsonify({"prediction": float(rul), "status": "ACTIVE", "message": "Deep Learning Analysis Complete"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- REPORT GENERATION ENDPOINTS ---

@app.route("/generate_report", methods=["POST"])
def api_generate_report():
    if not generate_maintenance_report: return jsonify({"error": "Report tools not installed"}), 500
    db = SessionLocal()
    try:
        # 1. Get Sensor Data
        # Try to get current simulation row, or fallback to latest
        sensor_row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()
        if not sensor_row:
             sensor_row = db.query(EngineSensorData).order_by(EngineSensorData.id.desc()).first()

        # 2. Get Prediction Data
        # If no predictions exist yet (just started), use defaults
        pred_row = db.query(Prediction).order_by(Prediction.id.desc()).first()
        
        if not sensor_row:
             return jsonify({"error": "No sensor data in database"}), 400

        # Build Data Dictionary (Safe Defaults)
        data = {
            "state": pred_row.state if pred_row else "UNKNOWN",
            "rul": pred_row.rul if pred_row else 0,
            "temperature": sensor_row.sensor_2 if sensor_row else 0,
            "pressure": sensor_row.sensor_7 if sensor_row else 0,
            "vibration": sensor_row.sensor_4 if sensor_row else 0
        }
        
        # 3. Generate Text
        report_text, error = generate_maintenance_report(data)
        if error: return jsonify({"error": error}), 500
        
        # 4. Save
        new_report = MaintenanceReport(
            engine_state=data['state'], 
            rul=data['rul'], 
            report_text=report_text, 
            sensor_summary=f"T:{data['temperature']:.0f}", 
            is_deleted=0
        )
        db.add(new_report)
        db.commit()
        
        return jsonify({
            "status": "success", 
            "report_id": new_report.id, 
            "text": report_text
        })
    except Exception as e:
        print(f"❌ Report Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/download_report/<int:report_id>", methods=["GET"])
def api_download_report(report_id):
    if not create_pdf_file: return "Disabled", 500
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if not report: return "Not found", 404
        reports_dir = os.path.join(project_root, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        pdf_path = create_pdf_file(report.report_text, {"state": report.engine_state, "rul": report.rul}, reports_dir)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return str(e), 500
    finally:
        db.close()

@app.route("/report_history", methods=["GET"])
def api_report_history():
    db = SessionLocal()
    try:
        reports = db.query(MaintenanceReport).filter(MaintenanceReport.is_deleted == 0).order_by(MaintenanceReport.timestamp.desc()).limit(10).all()
        return jsonify([{"id": r.id, "state": r.engine_state, "rul": r.rul, "time": str(r.timestamp)} for r in reports])
    finally:
        db.close()

@app.route("/view_report/<int:report_id>", methods=["GET"])
def api_view_report(report_id):
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if not report: return jsonify({"error": "Not found"}), 404
        return jsonify({"text": report.report_text, "state": report.engine_state, "rul": report.rul, "timestamp": str(report.timestamp)})
    finally:
        db.close()

@app.route("/delete_report/<int:report_id>", methods=["POST"])
def api_delete_report(report_id):
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if report: report.is_deleted = 1; db.commit()
        return jsonify({"status": "success"})
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting Flask Server...")
    app.run(host="0.0.0.0", port=8000, debug=True)