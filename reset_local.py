import os
import sys
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- FORCE LOCAL SETTINGS ---
# We ignore environment variables and force Localhost here
LOCAL_DB_URL = "postgresql://postgres:admin@localhost:5432/engine_health_db"

# Setup path to find your models
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.database.models import EngineSensorData

def restore_local_data():
    print("🔄 Connecting to LOCAL Database...")
    
    # 1. Connect
    engine = create_engine(LOCAL_DB_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 2. Clear old data to start fresh
        db.execute(text("TRUNCATE TABLE engine_sensor_data RESTART IDENTITY CASCADE;"))
        db.commit()
        print("🧹 Old data cleared.")

        # 3. Insert 5000 new rows
        print("🌱 Inserting 5000 rows...")
        
        for i in range(5000):
            row = EngineSensorData(
                op_setting_1=random.uniform(-0.005, 0.005),
                op_setting_2=random.uniform(-0.0005, 0.0005),
                op_setting_3=100.0,
                sensor_2=random.uniform(-2, 2),
                sensor_3=random.uniform(-2, 2),
                sensor_4=random.uniform(-2, 2),
                sensor_7=random.uniform(-2, 2),
                sensor_8=random.uniform(-2, 2),
                sensor_9=random.uniform(-2, 2),
                sensor_11=random.uniform(-2, 2),
                sensor_12=random.uniform(-2, 2),
                sensor_13=random.uniform(-2, 2),
                sensor_14=random.uniform(-2, 2),
                sensor_15=random.uniform(-2, 2),
                sensor_17=random.uniform(-2, 2),
                sensor_20=random.uniform(-2, 2),
                sensor_21=random.uniform(-2, 2)
            )
            db.add(row)
            
            # Commit in batches
            if (i + 1) % 500 == 0:
                db.commit()
                print(f"Inserted {i + 1} rows...")
        
        db.commit()
        print("✅ SUCCESS: Local Database is now full!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    restore_local_data()