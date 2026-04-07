import numpy as np
import pandas as pd
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
SEQUENCE_LENGTH = 30
DATA_PATH = 'data/processed/train_engineered.csv'
MODEL_PATH = 'artifacts/lstm_model.keras'
SCALER_PATH = 'artifacts/lstm_scaler.pkl'

# MUST MATCH APP.PY ORDER EXACTLY (17 Features)
FEATURE_COLUMNS = [
    'op_setting_1', 'op_setting_2', 'op_setting_3',
    'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9',
    'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 
    'sensor_17', 'sensor_20', 'sensor_21'
]

# ---------------------------------------------------------
# 1. DATA PREPARATION
# ---------------------------------------------------------
def create_sequences(X, y, time_steps=SEQUENCE_LENGTH):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X[i:(i + time_steps)])
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

def prepare_data():
    print("⚙️ Loading Processed Data...")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Select ONLY the 17 features defined above
    # Fill missing columns with 0 if they don't exist in CSV (safety)
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
            
    X = df[FEATURE_COLUMNS].values
    y = df['RUL'].values
    
    # 2. Scale Data
    print("🔄 Scaling Data...")
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save Scaler
    joblib.dump(scaler, SCALER_PATH)
    
    # 3. Create Sequences
    print(f"🧬 Creating Sequences (Window Size: {SEQUENCE_LENGTH})...")
    X_seq, y_seq = create_sequences(X_scaled, y)
    
    print(f"✅ Data Shape: {X_seq.shape}") # Should be (Samples, 30, 17)
    
    return X_seq, y_seq

# ---------------------------------------------------------
# 2. MODEL ARCHITECTURE
# ---------------------------------------------------------
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=64, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=64, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    
    print("🧠 Compiling Model...")
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# ---------------------------------------------------------
# 3. MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    X, y = prepare_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    
    print("🚀 Training LSTM Model...")
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    model.fit(X_train, y_train, epochs=20, batch_size=64, validation_split=0.1, callbacks=[early_stop], verbose=1)
    
    loss = model.evaluate(X_test, y_test)
    print(f"\n✅ Test Loss (MSE): {loss:.4f}")
    
    model.save(MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")
    print(f"💾 Scaler saved to {SCALER_PATH}")