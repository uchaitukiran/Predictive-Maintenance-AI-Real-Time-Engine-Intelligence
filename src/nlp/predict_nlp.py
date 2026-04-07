import joblib
import re
import os

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def predict_log_status(log_message):
    # 1. Load the trained model
    model_path = os.path.join('artifacts', 'nlp_log_classifier.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model not found. Please run train_nlp_model.py first.")
        return

    model = joblib.load(model_path)
    
    # 2. Clean the input
    clean_message = clean_text(log_message)
    
    # 3. Predict
    prediction = model.predict([clean_message])[0]
    
    # 4. Get Confidence (Probability)
    probs = model.predict_proba([clean_message])[0]
    confidence = max(probs)
    
    print(f"\n📝 Log: '{log_message}'")
    print(f"🔍 Prediction: {prediction}")
    print(f"📊 Confidence: {confidence*100:.2f}%")

if __name__ == "__main__":
    # Interactive Test
    print("=== NLP Log Classifier Test ===")
    
    # Test Case 1
    predict_log_status("Engine temperature is rising rapidly")
    
    # Test Case 2
    predict_log_status("All systems are operating normally")
    
    # Test Case 3
    predict_log_status("Fire detected in the turbine section!")
    
    # Test Case 4 (Your custom input)
    user_input = input("\nEnter your own log message: ")
    predict_log_status(user_input)