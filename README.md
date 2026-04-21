Predictive-Maintenance-AI-Real-Time-Engine-Intelligence
PythonFlaskTensorFlowPandasNumPyPostgreSQL

Project Overview
Predictive Maintenance AI is an end-to-end, enterprise-grade solution for predicting Remaining Useful Life (RUL) of Turbofan Engines. It bridges the gap between Data Science and Operational Intelligence by combining:

🧠 Deep Learning (LSTM): For sequence-based RUL prediction.
🤖 Machine Learning (XGBoost/GradientBoosting): For robust regression analysis.
💬 NLP & LLM (Groq): For intelligent log analysis and maintenance reasoning.
🎮 3D Visualization (Three.js): A real-time, interactive 3D dashboard for engine health monitoring.
Dataset Source: NASA C-MAPSS Turbofan Engine Degradation Data

3D Web App OutputFigure: Real-time 3D Engine Health Dashboard showing Warning State.

📊 Project Architecture
The system is designed in 5 distinct layers, moving from raw data to live deployment.

graph TD    %% STYLES    classDef data fill:#2c3e50,stroke:#fff,color:#fff;    classDef nb fill:#8e44ad,stroke:#fff,color:#fff;    classDef pipeline fill:#e67e22,stroke:#fff,color:#fff;    classDef artifact fill:#c0392b,stroke:#fff,color:#fff;    classDef backend fill:#16a085,stroke:#fff,color:#fff;    classDef frontend fill:#2980b9,stroke:#fff,color:#fff;    classDef future fill:#7f8c8d,stroke:#fff,stroke-dasharray: 5 5,color:#fff;    %% LAYER 1: DATA    subgraph L1 ["1. Data Engineering Layer"]        direction TB        A[("Raw Data<br>NASA C-MAPSS")]:::data --> B["01_Data_Engineering.ipynb"]:::nb        B --> C["02_Exploratory_Data_Analysis.ipynb"]:::nb        C --> D["03_Feature_Engineering.ipynb"]:::nb        D --> E[("Processed Data<br>train_engineered.csv")]:::data    end    %% LAYER 2: TRAINING    subgraph L2 ["2. Model Training Layer"]        direction TB        F["src/pipeline/<br>train_pipeline.py"]:::pipeline        G["src/components/<br>model_trainer.py"]:::pipeline                E --> F        F --> G        G --> H[("Artifacts/<br>GradientBoosting.pkl<br>LSTM.keras")]:::artifact    end    %% LAYER 3: AI & BACKEND    subgraph L3 ["3. Backend AI Layer"]        direction TB        I["src/api/<br>app.py"]:::backend        J[("PostgreSQL<br>Database")]:::data                K["NLP Analysis"]:::backend        L["LLM Integration<br>(Groq API)"]:::backend        M["Deep Learning<br>(LSTM)"]:::artifact                H --> I        I <--> J        I --> K        K --> L        I --> M    end    %% LAYER 4: VISUALIZATION    subgraph L4 ["4. Frontend Layer"]        direction TB        N["webapp/<br>viewer.js"]:::frontend        O["Three.js 3D Engine"]:::frontend                I -->|JSON Data| N        N --> O        O --> P["Real-Time Dashboard"]:::frontend    end    %% LAYER 5: OUTPUT    P --> Q(("LIVE OUTPUT<br>See Screenshot Above")):::frontend    %% LAYER 6: FUTURE    subgraph L5 ["5. DevOps & Future Scope"]        R["Docker Container"]:::future        S["RAG System<br>(Manuals Retrieval)"]:::future        T["Cloud Deploy<br>(AWS/GCP)"]:::future    end    I -.-> R    L -.-> S    R --> T

📁 Project Structure

Predictive-Maintenance-AI-Real-Time-Engine-Intelligence/
│
├── artifacts/                 # Saved Models & Preprocessors
│   ├── best_GradientBoosting.pkl
│   ├── lstm_model.keras
│   └── preprocessor.pkl
│
├── data/
│   ├── raw/                   # NASA Raw Text Files
│   └── processed/             # Cleaned CSV Data
│
├── notebooks/                 # Step 1: Data Engineering
│   ├── 01_Data_Engineering.ipynb
│   ├── 02_Exploratory_Data_Analysis.ipynb
│   └── 03_Feature_Engineering.ipynb
│
├── src/
│   ├── api/
│   │   └── app.py             # Step 3: Flask Backend Server
│   │
│   ├── components/            # Step 2: Training Components
│   │   ├── data_ingestion.py
│   │   ├── model_trainer.py
│   │   └── feature_engineering.py
│   │
│   ├── pipeline/              # Main Pipeline Entry Point
│   │   └── train_pipeline.py
│   │
│   ├── database/              # DB Models
│   └── utils/                 # Helpers (Reporting)
│
├── webapp/                    # Step 4: 3D Frontend
│   ├── index.html
│   ├── js/viewer.js           # Three.js Logic
│   └── css/style.css
│
├── requirements.txt
└── README.md

🛠️ Tech Stack
| Component | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | 3.10 |
| **Backend** | Flask | 3.0 |
| **Data** | Pandas | 2.3.3 |
| **Math** | NumPy | 1.26.4 |
| **AI / ML** | Scikit-Learn, XGBoost, LightGBM | 1.5.2, Latest |
| **Deep Learning** | TensorFlow (Keras) | 2.15 |
| **GenAI / NLP** | Groq API (LLM) | Latest |
| **3D Frontend** | Three.js | r128 |
| **Database** | PostgreSQL | 15 |



⚡ Quick Start

1. Clone & Setup

git clone https://github.com/uchaitukiran/Predictive-Maintenance-AI-Real-Time-Engine-Intelligence.git
cd Predictive-Maintenance-AI-Real-Time-Engine-Intelligence
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

2. Run Training Pipeline
Generates all model artifacts (.pkl, .keras).
python -m src.pipeline.train_pipeline

3. Start Web Server
python -m src.api.app

4. View in Browser
Open http://127.0.0.1:8000 to see the live 3D dashboard.

---

### **Step 2: Create the File and Push to GitHub**

Open your terminal (Command Prompt) inside your project folder (`D:\DATA SCIENCE with GEN AI\VS CODE\engine_health_monitoring_ai`) and run these commands one by one.

**1. Create the README file**
*(This creates the empty file)*
```cmd
type nul > README.md