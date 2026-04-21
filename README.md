# 🚀 Predictive Maintenance AI

### Real-Time Engine Health Monitoring using ML + LSTM + 3D Visualization

---

## 📸 Live 3D Dashboard

<p align="center">
  <img src="assets/images/dashboard.png" width="95%">
</p>

---

## 🧠 Project Overview

Predictive Maintenance AI is a real-time engine health monitoring system that combines **Machine Learning (ML)**, **Deep Learning (LSTM)**, and **Natural Language Processing (NLP)** with an interactive **3D Web Interface**.

The system predicts **Remaining Useful Life (RUL)** of turbofan engines using the **NASA C-MAPSS dataset** and visualizes engine state (**Good / Warning / Critical**) in a real-time 3D environment.

---

## 🧩 Project Architecture

<p align="center">
  <img src="assets/images/architecture.png" width="95%">
</p>

### 🔹 Flow Explanation

#### 1. Data Engineering
- Raw NASA turbofan data is ingested and cleaned  
- RUL (Remaining Useful Life) is calculated  
- Data is normalized and prepared  

#### 2. Feature Engineering
- Sensor features are selected and scaled  
- Optimized for real-time inference  

#### 3. Model Training Pipeline
- Multiple ML models trained:
  - Gradient Boosting
  - XGBoost
  - LightGBM
- Deep Learning:
  - LSTM for sequence prediction  
- Models saved as `.pkl` and `.keras`  

#### 4. Backend API (Flask)
- REST API handles:
  - `/predict` → ML predictions  
  - `/predict_lstm` → DL predictions  
  - `/analyze_log` → NLP log analysis  
  - `/generate_report` → PDF reports  

#### 5. AI Engine
- Combines ML + DL + NLP  
- Real-time inference engine  

#### 6. Data Storage
- PostgreSQL stores:
  - Sensor data  
  - Predictions  
  - Logs  

#### 7. Frontend (3D Web App)
- Built using **Three.js**
- Features:
  - Real-time engine visualization  
  - Color-based health states  
  - Live sensor gauges  
  - Fault simulation (fire/smoke effects)  

---

## 🤖 AI Models

| Model | Usage | File |
|------|------|------|
| Gradient Boosting | Primary RUL Prediction | `best_GradientBoosting.pkl` |
| XGBoost / LightGBM | Alternative Predictions | `XGBoost.pkl`, `LightGBM.pkl` |
| LSTM (Deep Learning) | Sequence RUL Prediction | `lstm_model.keras` |
| NLP Classifier | Log Analysis | `nlp_log_classifier.pkl` |

---

## 📁 Project Structure

```bash
Predictive-Maintenance-AI/
│
├── artifacts/            # Saved Models & Preprocessors
├── data/                 # Raw & Processed Data
├── notebooks/            # Data Engineering & EDA
│
├── src/
│   ├── api/              # Flask Backend
│   ├── components/       # ML Components
│   ├── pipeline/         # Training Pipelines
│   ├── database/         # DB Models
│   └── utils/            # Helpers
│
├── webapp/               # 3D Frontend
│   ├── index.html
│   ├── js/
│   └── css/
│
├── requirements.txt
└── README.md

⚙️ Tech Stack
 . Python 3.10
 . Flask
 . TensorFlow (LSTM)
 . Scikit-learn, XGBoost, LightGBM
 . PostgreSQL
 . Three.js

 🚀 Features
🔥 Real-time engine monitoring
🧠 LSTM-based RUL prediction
🤖 ML regression models
💬 NLP + LLM log analysis
🎮 Interactive 3D dashboard

⚡ Quick Start
git clone https://github.com/your-repo.git
cd Predictive-Maintenance-AI-Real-Time-Engine-Intelligence
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Run:
python -m src.pipeline.train_pipeline
python -m src.api.app

Open:
http://127.0.0.1:8000

🔮 Future Scope
RAG-based maintenance assistant
Docker containerization
Cloud deployment (AWS / GCP)
Real-time streaming integration