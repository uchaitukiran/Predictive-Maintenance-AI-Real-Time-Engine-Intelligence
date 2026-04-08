import numpy as np
import pandas as pd
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
SEQUENCE_LENGTH = 30
DATA_PATH = 'data/processed/train_engineered.csv'
MODEL_PATH = 'artifacts/lstm_model.keras'
SCALER_PATH = 'artifacts/lstm_scaler.pkl'
Y_SCALER_PATH = 'artifacts/lstm_y_scaler.pkl'

FEATURE_COLUMNS = [
    'op_setting_1', 'op_setting_2', 'op_setting_3',
    'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9',
    'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 
    'sensor_17', 'sensor_20', 'sensor_21'
]

def create_sequences(X, y, time_steps=SEQUENCE_LENGTH):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X[i:(i + time_steps)])
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

def prepare_data():
    print("⚙️ Loading Processed Data...")
    df = pd.read_csv(DATA_PATH)
    
    for col in FEATURE_COLUMNS:
        if col not in df.columns: df[col] = 0
            
    X = df[FEATURE_COLUMNS].values
    y = df['RUL'].values.reshape(-1, 1)
    
    # Scale X
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)
    
    # Scale Y (Target)
    y_scaler = MinMaxScaler()
    y_scaled = y_scaler.fit_transform(y)
    joblib.dump(y_scaler, Y_SCALER_PATH)
    
    print(f"🧬 Creating Sequences...")
    X_seq, y_seq = create_sequences(X_scaled, y_scaled)
    
    return X_seq, y_seq

if __name__ == "__main__":
    X, y = prepare_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='linear'))
    
    model.compile(optimizer='adam', loss='mse')
    
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
    
    print("🚀 Training LSTM Model...")
    model.fit(X_train, y_train, epochs=50, batch_size=64, validation_split=0.1, callbacks=[early_stop, reduce_lr], verbose=1)
    
    loss = model.evaluate(X_test, y_test)
    print(f"\n✅ Test Loss (MSE): {loss:.4f}")
    
    model.save(MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")
    print(f"💾 Y Scaler saved to {Y_SCALER_PATH}")