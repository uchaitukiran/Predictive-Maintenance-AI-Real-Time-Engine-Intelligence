from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import os
import traceback

app = Flask(__name__, template_folder='webapp')

# ---------------------------------------------------------
# 1. LOAD MODEL ARTIFACT
# ---------------------------------------------------------
MODEL_PATH = os.path.join('artifacts', 'best_GradientBoosting.pkl')
model = None

try:
    # Check if file exists
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ SUCCESS: Model loaded from {MODEL_PATH}")
    else:
        print(f"❌ ERROR: File not found at {MODEL_PATH}")
        print("Current working directory:", os.getcwd())
        print("Files in current dir:", os.listdir('.'))
except Exception as e:
    print(f"❌ ERROR loading model: {e}")
    traceback.print_exc()

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Extract features
        # IMPORTANT: Ensure the order matches your model training columns
        # Example: [temp, pressure, vibration]
        features = np.array([
            data.get('temperature', 80.0),
            data.get('pressure', 30.0),
            data.get('vibration', 0.3)
        ]).reshape(1, -1)

        # -------------------------------------------------
        # PREDICTION LOGIC
        # -------------------------------------------------
        if model:
            # Predict using the loaded model
            prediction = model.predict(features)
            
            # Handle different output types (array vs scalar)
            if isinstance(prediction, np.ndarray):
                rul = float(prediction[0])
            else:
                rul = float(prediction)
                
            print(f"Predicted RUL: {rul}")
        else:
            # Fallback if model failed to load
            import random
            rul = random.uniform(50, 150)
            print("Warning: Using Dummy Data (Model not loaded)")
            
        # Determine State based on RUL
        if rul > 100:
            state = "GOOD"
        elif rul > 50:
            state = "WARNING"
        else:
            state = "CRITICAL"
            
        # -------------------------------------------------
        # RETURN RESPONSE
        # Keys MUST match frontend: "state" and "Predicted_RUL"
        return jsonify({
            "state": state, 
            "Predicted_RUL": rul
        })

    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)