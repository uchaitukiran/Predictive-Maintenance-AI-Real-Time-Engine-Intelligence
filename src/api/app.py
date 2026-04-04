from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import sys
import os

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.insert(0, project_root)

# Import Database Components
from src.database.db import SessionLocal
from src.database.models import EngineSensorData, Prediction
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

app = Flask(__name__, 
            static_folder=os.path.join(project_root, "webapp"),
            template_folder=os.path.join(project_root, "webapp"),
            static_url_path='') 

CORS(app)

# API Setup
api = Api(app, version='1.0', title='Engine Health Monitoring API',
          description='MNC Level API for Predictive Maintenance',
          doc='/docs')
ns = api.namespace('', description='Operations')

# ---------------------------------------------------------
# GLOBAL SIMULATION COUNTER
# ---------------------------------------------------------
current_simulation_id = 0

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

# NEW: Endpoint to Reset Simulation to Row 1
@app.route("/reset", methods=['GET'])
def reset_simulation():
    global current_simulation_id
    current_simulation_id = 0
    return jsonify({'status': 'reset', 'message': 'Simulation restarted from Row 1'})

@app.route("/get_real_data", methods=['GET'])
def get_real_data():
    global current_simulation_id
    db = SessionLocal()
    try:
        # Increment ID
        current_simulation_id += 1
        
        # Fetch row
        row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()
        
        # If end of data, loop back to 1
        if not row:
            current_simulation_id = 1
            row = db.query(EngineSensorData).filter(EngineSensorData.id == current_simulation_id).first()

        if row:
            return jsonify({
                'id': row.id,
                'op_setting_1': row.op_setting_1,
                'op_setting_2': row.op_setting_2,
                'op_setting_3': row.op_setting_3,
                'sensor_2': row.sensor_2,
                'sensor_3': row.sensor_3,
                'sensor_4': row.sensor_4,
                'sensor_7': row.sensor_7,
                'sensor_8': row.sensor_8,
                'sensor_9': row.sensor_9,
                'sensor_11': row.sensor_11,
                'sensor_12': row.sensor_12,
                'sensor_13': row.sensor_13,
                'sensor_14': row.sensor_14,
                'sensor_15': row.sensor_15,
                'sensor_17': row.sensor_17,
                'sensor_20': row.sensor_20,
                'sensor_21': row.sensor_21
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
            
            # Prepare Data
            custom_data = CustomData(
                op_setting_1=float(data.get('op_setting_1', 0)),
                op_setting_2=float(data.get('op_setting_2', 0)),
                op_setting_3=float(data.get('op_setting_3', 0)),
                sensor_2=float(data.get('sensor_2', 0)),
                sensor_3=float(data.get('sensor_3', 0)),
                sensor_4=float(data.get('sensor_4', 0)),
                sensor_7=float(data.get('sensor_7', 0)),
                sensor_8=float(data.get('sensor_8', 0)),
                sensor_9=float(data.get('sensor_9', 0)),
                sensor_11=float(data.get('sensor_11', 0)),
                sensor_12=float(data.get('sensor_12', 0)),
                sensor_13=float(data.get('sensor_13', 0)),
                sensor_14=float(data.get('sensor_14', 0)),
                sensor_15=float(data.get('sensor_15', 0)),
                sensor_17=float(data.get('sensor_17', 0)),
                sensor_20=float(data.get('sensor_20', 0)),
                sensor_21=float(data.get('sensor_21', 0))
            )
            
            pred_df = custom_data.get_data_as_data_frame()
            predict_pipeline = PredictPipeline()
            results = predict_pipeline.predict(pred_df)
            rul_value = float(results[0])

            # Determine State
            if rul_value > 100:
                state = "GOOD"
            elif rul_value > 30:
                state = "WARNING"
            else:
                state = "CRITICAL"

            # Log to DB (Optional)
            new_pred = Prediction(
                state=state,
                rul=rul_value,
                temperature=data.get('sensor_2', 0),
                pressure=data.get('sensor_7', 0),
                vibration=data.get('sensor_4', 0)
            )
            db.add(new_pred)
            db.commit()

            return {
                'Predicted_RUL': rul_value,
                'state': state
            }

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {'error': str(e)}, 500
        finally:
            db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)