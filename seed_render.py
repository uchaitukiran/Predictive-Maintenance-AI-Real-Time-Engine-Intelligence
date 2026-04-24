import os
import sys
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- CONFIGURATION ---
# REPLACE THIS WITH YOUR EXTERNAL DATABASE URL FROM RENDER
RENDER_URL = "postgresql://engine_health_db_user:tG3dHmaOtqqF2YfN3z4BQvibiZO23oTl@dpg-d7lg3lm7r5hc739m1230-a.singapore-postgres.render.com/engine_health_db"

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.database.models import EngineSensorData

def run():
    print("🌍 Connecting to RENDER Database...")
    engine = create_engine(RENDER_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Check if data exists
        if db.query(EngineSensorData).count() > 100:
            print("Data already exists. Skipping.")
            return

        print("🌱 Seeding 5000 rows...")
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
            if (i + 1) % 500 == 0:
                db.commit()
                print(f"Inserted {i + 1}...")
        
        db.commit()
        print("✅ SUCCESS: Render Database Populated!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()