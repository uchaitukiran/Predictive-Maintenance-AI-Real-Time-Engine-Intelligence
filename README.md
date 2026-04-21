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

It bridges the gap between **Data Science** and **Operational Intelligence** by combining:

- 🧠 **Deep Learning (LSTM)** → Sequence-based RUL prediction  
- 🤖 **Machine Learning (XGBoost / GradientBoosting)** → Robust regression analysis  
- 💬 **NLP & LLM (Groq)** → Intelligent log analysis & reasoning  
- 🎮 **3D Visualization (Three.js)** → Real-time interactive engine monitoring  

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

bash
Predictive-Maintenance-AI/
│
├── artifacts/              # Saved Models & Preprocessors
├── data/                   # Raw & Processed Data
├── notebooks/              # Data Engineering & EDA
│
├── src/
│   ├── api/                # Flask Backend
│   ├── components/         # ML Components
│   ├── pipeline/           # Training Pipelines
│   ├── database/           # DB Models
│   └── utils/              # Helpers
│
├── webapp/                 # 3D Frontend
│   ├── index.html
│   ├── js/
│   └── css/
│
├── requirements.txt
└── README.md

---

## ⚙️ Tech Stack

> Core technologies used in this project

**Python 3.10**
**Flask (Backend API)**
**TensorFlow (LSTM)**
**Scikit-learn, XGBoost, LightGBM**
**PostgreSQL (Database)**
**Three.js (3D Visualization)**

---

## ✨ Features

> Key capabilities of the system

🔥 **Real-time engine monitoring**
🧠 **LSTM-based RUL prediction**
🤖 **Multiple ML regression models**
💬 **NLP + LLM log analysis**
🎮 **Interactive 3D dashboard**

---

## ⚡ Quick Start

### 1️⃣ Clone & Setup

bash
git clone https://github.com/your-username/your-repo.git
cd Predictive-Maintenance-AI-Real-Time-Engine-Intelligence
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

---

## 2️⃣ Run Application

> Start training and backend services

bash
python -m src.pipeline.train_pipeline
python -m src.api.app

## 3️⃣ Open in Browser

> Access the live 3D dashboard

👉 **http://127.0.0.1:8000**

---

## 🔮 Future Scope

> Planned enhancements

📚 **RAG-based maintenance assistant**
🐳 **Docker containerization**
☁️ **Cloud deployment (AWS / GCP)**
⚡ **Real-time data streaming integration**


## 📜 License

> Usage and distribution

This project is licensed under the **MIT License**.