import os
import sys
import random

# Setup path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db import SessionLocal, engine, Base
from src.database.models import EngineSensorData

def run_seed():
    print("🔄 Connecting to Database...")
    
    # 1. Create Tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables verified.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return

    db = SessionLocal()
    try:
        # Check count
        count = db.query(EngineSensorData).count()
        if count > 4000:
            print(f"Data already exists ({count} rows). Skipping.")
            return

        print("🌱 Seeding 5000 rows... please wait.")
        
        batch_size = 500
        total_rows = 5000
        
        # Loop to create 5000 rows
        for i in range(total_rows):
            row = EngineSensorData(
                op_setting_1=random.uniform(-0.005, 0.005),
                op_setting_2=random.uniform(-0.0005, 0.0005),
                op_setting_3=100.0,
                sensor_2=random.uniform(-2, 2),  # Temp (Normalized)
                sensor_3=random.uniform(-2, 2),
                sensor_4=random.uniform(-2, 2),  # Vib (Normalized)
                sensor_7=random.uniform(-2, 2),  # Pres (Normalized)
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
            
            # Commit in batches to save memory
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"Inserted {i + 1} rows...")
        
        db.commit()
        print("✅ SUCCESS: Inserted 5000 rows!")

    except Exception as e:
        print(f"❌ Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()