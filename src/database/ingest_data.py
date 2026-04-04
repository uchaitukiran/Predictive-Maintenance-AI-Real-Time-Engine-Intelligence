import sys
import os
import pandas as pd

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.db import SessionLocal, engine
from src.database.models import EngineSensorData

def ingest_csv_to_db():
    print("⚙️ Starting Data Ingestion...")
    
    # 1. Locate CSV
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            "data", "processed", "train_engineered.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # 2. Open DB Session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(EngineSensorData).count() > 0:
            print("✅ Database already populated. Skipping.")
            return

        # 3. Insert Data Row by Row
        # We use a slice df.head(1000) to keep the DB small for demo, or remove slice for full data
        data_to_insert = []
        
        for _, row in df.iterrows():
            record = EngineSensorData(
                cycle=row.get('cycle', 0),
                op_setting_1=row.get('op_setting_1', 0),
                op_setting_2=row.get('op_setting_2', 0),
                op_setting_3=row.get('op_setting_3', 0),
                sensor_2=row.get('sensor_2', 0),
                sensor_3=row.get('sensor_3', 0),
                sensor_4=row.get('sensor_4', 0),
                sensor_7=row.get('sensor_7', 0),
                sensor_8=row.get('sensor_8', 0),
                sensor_9=row.get('sensor_9', 0),
                sensor_11=row.get('sensor_11', 0),
                sensor_12=row.get('sensor_12', 0),
                sensor_13=row.get('sensor_13', 0),
                sensor_14=row.get('sensor_14', 0),
                sensor_15=row.get('sensor_15', 0),
                sensor_17=row.get('sensor_17', 0),
                sensor_20=row.get('sensor_20', 0),
                sensor_21=row.get('sensor_21', 0)
            )
            data_to_insert.append(record)
        
        db.bulk_save_objects(data_to_insert)
        db.commit()
        print(f"✅ SUCCESS: Inserted {len(data_to_insert)} rows into Database.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_csv_to_db()