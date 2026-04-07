import pandas as pd
import re
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

def clean_text(text):
    """
    Basic text cleaning:
    - Lowercase
    - Remove special characters
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def train_log_classifier():
    print("⚙️ Loading Engine Logs...")
    
    # 1. Load Data
    df = pd.read_csv('data/raw/engine_logs.csv')
    
    # 2. Preprocess
    print("🧹 Cleaning text data...")
    df['clean_message'] = df['log_message'].apply(clean_text)
    
    X = df['clean_message']
    y = df['status']
    
    # 3. Split Data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Build Pipeline
    # Pipeline: TF-IDF (Convert text to numbers) -> Logistic Regression (Classifier)
    print("🤖 Training NLP Model...")
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression(solver='liblinear'))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # 5. Evaluate
    print("✅ Training Complete. Evaluating Model...")
    y_pred = pipeline.predict(X_test)
    
    print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # 6. Save Model
        # 6. Save Model
    model_dir = 'artifacts'  # CHANGE: Save to artifacts folder
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'nlp_log_classifier.pkl')
    
    joblib.dump(pipeline, model_path)
    print(f"\n💾 Model saved to: {model_path}")

if __name__ == "__main__":
    train_log_classifier()