import os
import sys
import random

# Setup path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db import engine
from sqlalchemy import text

# ---------------------------------------------------------
# STEP 1: CREATE TABLE MANUALLY (FIXES UNDEFINED TABLE ERROR)
# ---------------------------------------------------------
def create_table():
    print("🔄 Creating Table in Cloud Database...")
    try:
        with engine.connect() as conn:
            # This SQL command creates the table exactly how your model expects it
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS engine_sensor_data (
                    id SERIAL PRIMARY KEY,
                    op_setting_1 FLOAT,
                    op_setting_2 FLOAT,
                    op_setting_3 FLOAT,
                    sensor_2 FLOAT,
                    sensor_3 FLOAT,
                    sensor_4 FLOAT,
                    sensor_7 FLOAT,
                    sensor_8 FLOAT,
                    sensor_9 FLOAT,
                    sensor_11 FLOAT,
                    sensor_12 FLOAT,
                    sensor_13 FLOAT,
                    sensor_14 FLOAT,
                    sensor_15 FLOAT,
                    sensor_17 FLOAT,
                    sensor_20 FLOAT,
                    sensor_21 FLOAT
                );
            """))
            conn.commit()
        print("✅ Table Created Successfully!")
        return True
    except Exception as e:
        print(f"❌ Table Creation Error: {e}")
        return False

# ---------------------------------------------------------
# STEP 2: SEED DATA (INSERT 5000 ROWS)
# ---------------------------------------------------------
def seed_data():
    from src.database.db import SessionLocal
    from src.database.models import EngineSensorData
    
    db = SessionLocal()
    try:
        # Check if data exists
        if db.query(EngineSensorData).count() > 0:
            print("Data already exists. Skipping insert.")
            return

        print("🌱 Inserting 5000 rows...")
        batch_size = 500
        total_rows = 5000
        
        for i in range(total_rows):
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
            
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"Inserted {i + 1} rows...")
        
        db.commit()
        print("✅ SUCCESS: All data inserted!")

    except Exception as e:
        print(f"❌ Seeding Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Run Step 1 then Step 2
    if create_table():
        seed_data()