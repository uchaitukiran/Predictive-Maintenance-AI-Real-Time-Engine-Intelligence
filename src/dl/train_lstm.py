import numpy as np
import pandas as pd
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Configuration
SEQUENCE_LENGTH = 30
DATA_PATH = 'data/processed/train_engineered.csv'
MODEL_PATH = 'artifacts/lstm_model.keras'
SCALER_PATH = 'artifacts/lstm_scaler.pkl'
Y_SCALER_PATH = 'artifacts/lstm_y_scaler.pkl'

# Automatic Mapper: App Name -> [Possible CSV Names]
COLUMN_MAP = {
    'op_setting_1': ['op_setting_1', 'setting1', 'op1'],
    'op_setting_2': ['op_setting_2', 'setting2', 'op2'],
    'op_setting_3': ['op_setting_3', 'setting3', 'op3'],
    'sensor_2': ['sensor_2', 's2', 'T30'],
    'sensor_3': ['sensor_3', 's3', 'T50'],
    'sensor_4': ['sensor_4', 's4', 'P30'],
    'sensor_7': ['sensor_7', 's7', 'P50'],
    'sensor_8': ['sensor_8', 's8', 'P21'],
    'sensor_9': ['sensor_9', 's9'],
    'sensor_11': ['sensor_11', 's11'],
    'sensor_12': ['sensor_12', 's12'],
    'sensor_13': ['sensor_13', 's13'],
    'sensor_14': ['sensor_14', 's14'],
    'sensor_15': ['sensor_15', 's15'],
    'sensor_17': ['sensor_17', 's17'],
    'sensor_20': ['sensor_20', 's20'],
    'sensor_21': ['sensor_21', 's21'],
    'RUL': ['RUL', 'rul', 'Remaining_Useful_Life']
}

def find_column(df, target_name):
    """Tries to find a column matching target name or its variants."""
    if target_name in df.columns:
        return target_name
    if target_name in COLUMN_MAP:
        for variant in COLUMN_MAP[target_name]:
            if variant in df.columns:
                return variant
    return None

def create_sequences(X, y, time_steps=SEQUENCE_LENGTH):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X[i:(i + time_steps)])
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

if __name__ == "__main__":
    print("⚙️ Loading Data...")
    df = pd.read_csv(DATA_PATH)
    
    # --- PRINT HEADERS FOR DEBUG ---
    print(f"🔍 Found Columns in CSV: {df.columns.tolist()[:10]}...")
    
    # --- SMART COLUMN FINDER ---
    feature_cols = []
    targets = ['op_setting_1', 'op_setting_2', 'op_setting_3',
               'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9',
               'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 
               'sensor_17', 'sensor_20', 'sensor_21']
    
    valid_data = True
    
    for t in targets:
        col = find_column(df, t)
        if col:
            feature_cols.append(col)
        else:
            print(f"❌ Missing Column: {t}. Filling with 0.")
            df[t] = 0
            feature_cols.append(t)
            valid_data = False
            
    # Find Target (RUL)
    rul_col = find_column(df, 'RUL')
    if not rul_col:
        print("❌ FATAL: RUL column not found!")
        exit()

    X = df[feature_cols].values
    y = df[rul_col].values

    # Check Data Integrity
    print(f"📊 Data Stats -> Min: {y.min():.2f}, Max: {y.max():.2f}, Mean: {y.mean():.2f}")
    
    if y.max() < 1.0:
        print("❌ ERROR: Target (RUL) data is invalid (all zeros).")
        print("➡️ SOLUTION: Please run '03_feature_engineering.ipynb' notebook to generate the correct CSV.")
        exit()

    # Scale X
    scaler_x = MinMaxScaler()
    X_scaled = scaler_x.fit_transform(X)
    joblib.dump(scaler_x, SCALER_PATH)

    # Scale Y
    scaler_y = MinMaxScaler()
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1))
    joblib.dump(scaler_y, Y_SCALER_PATH)
    print(f"✅ Scalers Saved. Y Range: {scaler_y.data_min_[0]:.1f} to {scaler_y.data_max_[0]:.1f}")

    # Create Sequences
    print("🧬 Creating Sequences...")
    X_seq, y_seq = create_sequences(X_scaled, y_scaled)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, shuffle=False)

    # Build Model
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='linear'))
    
    model.compile(optimizer='adam', loss='mse')
    
    print("🚀 Training...")
    es = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=30, batch_size=64, validation_split=0.2)
    model.add(Dense(1, activation='linear'))
    
    model.compile(optimizer='adam', loss='mse')
    
    print("🚀 Training...")
    es = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=30, batch_size=64, validation_split=0.1, callbacks=[es], verbose=1)
    
    # Evaluate
    loss = model.evaluate(X_test, y_test)
    print(f"📉 Test Loss: {loss:.4f}")

    # Sanity Check
    pred_scaled = model.predict(X_test[0:1])
    pred_real = scaler_y.inverse_transform(pred_scaled)
    print(f"🔎 SANITY CHECK: Real RUL={pred_real[0][0]:.2f}")

    if pred_real[0][0] < 1.0:
        print("⚠️ Warning: Model predicted 0. Training data might still be corrupt.")
    else:
        model.save(MODEL_PATH)
        print(f"💾 Model Saved to {MODEL_PATH}")