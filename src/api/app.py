from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import sys
import os
import joblib
import re
import numpy as np
from collections import deque
# DISABLED TENSORFLOW TO SAVE MEMORY (LSTM model is corrupt anyway)
# from tensorflow.keras.models import load_model 
import threading

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.insert(0, project_root)

# Import Components
from src.database.db import SessionLocal, Base, engine
from src.database.models import EngineSensorData, Prediction, MaintenanceReport
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

# ---------------------------------------------------------
# 1. INITIALIZE DATABASE TABLES
# ---------------------------------------------------------
print("🚀 Initializing Database Tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database Tables Ready.")
except Exception as e:
    print(f"❌ DB Init Error: {e}")

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

# ---------------------------------------------------------
# DATA TRANSLATOR
# ---------------------------------------------------------
def to_real_value(norm_val, sensor_type):
    if sensor_type == 'temp': return (norm_val + 3) * 50 + 600
    if sensor_type == 'press': return (norm_val + 3) * 50 + 400
    if sensor_type == 'vib': return (norm_val + 3) * 50 + 1000
    return norm_val

def to_norm_value(real_val, sensor_type):
    if sensor_type == 'temp': return (real_val - 600) / 50 - 3
    if sensor_type == 'press': return (real_val - 400) / 50 - 3
    if sensor_type == 'vib': return (real_val - 1000) / 50 - 3
    return real_val

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

# ---------------------------------------------------------
# RAG LAZY LOADER (SAVES RAM)
# ---------------------------------------------------------
@app.route("/rag_chat", methods=["POST"])
def rag_chat():
    db = SessionLocal()
    try:
        data = request.get_json()
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # LAZY LOAD RAG
        try:
            print("🔄 Lazy Loading RAG Models...")
            from src.rag.retriever import ask_question
            print("✅ RAG Models Loaded.")
        except Exception as import_error:
            print(f"❌ RAG Import Error: {import_error}")
            return jsonify({"error": "AI Brain failed to start."}), 500

        last_pred = db.query(Prediction).order_by(Prediction.id.desc()).first()
        
        live_context = None
        if last_pred:
            live_context = {
                "state": last_pred.state, "rul": last_pred.rul,
                "temperature": last_pred.temperature, "pressure": last_pred.pressure,
                "vibration": last_pred.vibration
            }
        
        answer, sources = ask_question(query, live_context)
        return jsonify({"answer": answer, "sources": sources})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# API Setup
api = Api(app, version='1.0', title='Engine Health Monitoring API', doc='/docs')
ns = api.namespace('', description='Operations')

# Global Variables
current_simulation_id = 0

# NLP Model Loading
NLP_MODEL_PATH = os.path.join(project_root, "artifacts", "nlp_log_classifier.pkl")
nlp_model = joblib.load(NLP_MODEL_PATH) if os.path.exists(NLP_MODEL_PATH) else None
if nlp_model: print("✅ NLP Model Loaded.")

def clean_text_nlp(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# ---------------------------------------------------------
# LSTM DISABLED TO SAVE MEMORY
# ---------------------------------------------------------
# The model file is corrupt. Importing TensorFlow crashes memory.
lstm_model = None
lstm_scaler = None
y_scaler = None
print("⚠️ LSTM DISABLED: Model file corrupt. Saving RAM.")

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
        if not row:
            current_simulation_id = 1
            row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()

        if row:
            real_temp = to_real_value(row.sensor_2, 'temp')
            real_press = to_real_value(row.sensor_7, 'press')
            real_vib = to_real_value(row.sensor_4, 'vib')

            return jsonify({
                'id': row.id, 'op_setting_1': row.op_setting_1, 'op_setting_2': row.op_setting_2, 'op_setting_3': row.op_setting_3,
                'sensor_2': real_temp, 'sensor_3': row.sensor_3, 'sensor_4': real_vib, 'sensor_7': real_press,
                'sensor_8': row.sensor_8, 'sensor_9': row.sensor_9, 'sensor_11': row.sensor_11, 'sensor_12': row.sensor_12, 
                'sensor_13': row.sensor_13, 'sensor_14': row.sensor_14, 'sensor_15': row.sensor_15, 'sensor_17': row.sensor_17,
                'sensor_20': row.sensor_20, 'sensor_21': row.sensor_21
            })
        else:
            return jsonify({'error': 'Database is empty'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@ns.route('/predict')
class PredictResource(Resource):
    def post(self):
        db = SessionLocal()
        try:
            data = request.get_json()
            norm_temp = to_norm_value(float(data.get('sensor_2', 0)), 'temp')
            norm_press = to_norm_value(float(data.get('sensor_7', 0)), 'press')
            norm_vib = to_norm_value(float(data.get('sensor_4', 0)), 'vib')

            custom_data = CustomData(
                op_setting_1=float(data.get('op_setting_1', 0)), op_setting_2=float(data.get('op_setting_2', 0)), 
                op_setting_3=float(data.get('op_setting_3', 0)), sensor_2=norm_temp, sensor_3=float(data.get('sensor_3', 0)), 
                sensor_4=norm_vib, sensor_7=norm_press, sensor_8=float(data.get('sensor_8', 0)), sensor_9=float(data.get('sensor_9', 0)),
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

            new_pred = Prediction(state=state, rul=rul_value, temperature=float(data.get('sensor_2', 0)),
                                  pressure=float(data.get('sensor_7', 0)), vibration=float(data.get('sensor_4', 0)))
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
    # Endpoint returns Unavailable because model is disabled
    return jsonify({"prediction": 0, "status": "DISABLED", "message": "LSTM is disabled to save memory."})

# --- REPORT ENDPOINTS (Keep your existing report code here) ---
@app.route("/generate_report", methods=["POST"])
def api_generate_report():
    if not generate_maintenance_report: return jsonify({"error": "Report tools not installed"}), 500
    db = SessionLocal()
    try:
        pred_row = db.query(Prediction).order_by(Prediction.id.desc()).first()
        if not pred_row: return jsonify({"error": "No prediction data available"}), 400
        data = {"state": pred_row.state, "rul": pred_row.rul, "temperature": pred_row.temperature, "pressure": pred_row.pressure, "vibration": pred_row.vibration}
        report_text, error = generate_maintenance_report(data)
        if error: return jsonify({"error": error}), 500
        new_report = MaintenanceReport(engine_state=data['state'], rul=data['rul'], report_text=report_text, sensor_summary=f"T:{data['temperature']:.0f} P:{data['pressure']:.0f}", is_deleted=0)
        db.add(new_report); db.commit()
        return jsonify({"status": "success", "report_id": new_report.id, "text": report_text})
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: db.close()

@app.route("/download_report/<int:report_id>", methods=["GET"])
def api_download_report(report_id):
    if not create_pdf_file: return "Disabled", 500
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if not report: return "Not found", 404
        reports_dir = os.path.join(project_root, "reports"); os.makedirs(reports_dir, exist_ok=True)
        pdf_path = create_pdf_file(report.report_text, {"state": report.engine_state, "rul": report.rul}, reports_dir)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally: db.close()

@app.route("/report_history", methods=["GET"])
def api_report_history():
    db = SessionLocal()
    try:
        reports = db.query(MaintenanceReport).filter(MaintenanceReport.is_deleted == 0).order_by(MaintenanceReport.timestamp.desc()).limit(10).all()
        return jsonify([{"id": r.id, "state": r.engine_state, "rul": r.rul, "time": str(r.timestamp)} for r in reports])
    finally: db.close()

@app.route("/view_report/<int:report_id>", methods=["GET"])
def api_view_report(report_id):
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if not report: return jsonify({"error": "Not found"}), 404
        return jsonify({"text": report.report_text, "state": report.engine_state, "rul": report.rul, "timestamp": str(report.timestamp)})
    finally: db.close()

@app.route("/delete_report/<int:report_id>", methods=["POST"])
def api_delete_report(report_id):
    db = SessionLocal()
    try:
        report = db.query(MaintenanceReport).filter(MaintenanceReport.id == report_id).first()
        if report: report.is_deleted = 1; db.commit()
        return jsonify({"status": "success"})
    finally: db.close()

if __name__ == "__main__":
    print("🚀 Starting Flask Server (Local)...")
    app.run(host="0.0.0.0", port=8000, debug=True)