# Predictive-Maintenance-AI-Real-Time-Engine-Intelligence

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange)
![Pandas](https://img.shields.io/badge/Pandas-2.3.3-blue)
![NumPy](https://img.shields.io/badge/NumPy-1.26.4-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)

---

## 🚀 Project Overview

Predictive Maintenance AI is an **end-to-end, enterprise-grade solution** for predicting **Remaining Useful Life (RUL)** of turbofan engines.

- 🧠 Deep Learning (LSTM) → Sequence-based RUL prediction  
- 🤖 Machine Learning (XGBoost / GradientBoosting) → Robust regression  
- 💬 NLP & LLM (Groq) → Log analysis & reasoning  
- 🎮 3D Visualization (Three.js) → Real-time engine monitoring  

---

## 📸 3D Web App Output

<p align="center">
  <img src="assets/images/dashboard.png" width="95%">
</p>

> Real-time 3D Engine Health Dashboard showing **Warning State**

---

## 🧠 Project Architecture

<p align="center">
  <img src="assets/images/architecture.png" width="95%">
</p>

---

### 🔹 Flow Explanation

#### 1. Data Engineering
- Raw NASA turbofan data is ingested and cleaned  
- RUL is calculated  
- Data is normalized  

#### 2. Feature Engineering
- Sensor features selected and scaled  
- Optimized for real-time inference  

#### 3. Model Training Pipeline
- Gradient Boosting  
- XGBoost  
- LightGBM  
- LSTM (Deep Learning)  
- Models saved as `.pkl` and `.keras`  

#### 4. Backend API (Flask)
- `/predict` → ML predictions  
- `/predict_lstm` → DL predictions  
- `/analyze_log` → NLP log analysis  
- `/generate_report` → PDF reports  

#### 5. AI Engine
- ML + DL + NLP combined  
- Real-time inference  

#### 6. Data Storage
- PostgreSQL stores:
  - Sensor data  
  - Predictions  
  - Logs  

#### 7. Frontend (3D Web App)
- Built using Three.js  
- Real-time engine visualization  
- Health state coloring  
- Live gauges  
- Fault simulation  

---

## 🤖 AI Models

| Model | Usage | File |
|------|------|------|
| Gradient Boosting | Primary RUL Prediction | `best_GradientBoosting.pkl` |
| XGBoost / LightGBM | Alternative Predictions | `XGBoost.pkl`, `LightGBM.pkl` |
| LSTM | Sequence Prediction | `lstm_model.keras` |
| NLP Classifier | Log Analysis | `nlp_log_classifier.pkl` |

---

## 📁 Project Structure

```bash
Predictive-Maintenance-AI/
├── artifacts/
├── data/
├── notebooks/
├── src/
│   ├── api/
│   ├── components/
│   ├── pipeline/
│   ├── database/
│   └── utils/
├── webapp/
│   ├── index.html
│   ├── js/
│   └── css/
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

- Python 3.10  
- Flask  
- TensorFlow  
- Scikit-learn, XGBoost, LightGBM  
- PostgreSQL  
- Three.js  

---

## ✨ Features

- 🔥 Real-time engine monitoring  
- 🧠 LSTM-based RUL prediction  
- 🤖 Multiple ML models  
- 💬 NLP + LLM analysis  
- 🎮 3D dashboard  

---

## ⚡ Quick Start

### 1️⃣ Clone & Setup

```bash
git clone https://github.com/your-username/your-repo.git
cd Predictive-Maintenance-AI-Real-Time-Engine-Intelligence
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2️⃣ Run Application

```bash
python -m src.pipeline.train_pipeline
python -m src.api.app
```

---

### 3️⃣ Open in Browser

👉 http://127.0.0.1:8000

---

## 🔮 Future Scope

- 📚 RAG-based assistant  
- 🐳 Docker  
- ☁️ Cloud deployment  
- ⚡ Real-time streaming  

---

## 📜 License

MIT License