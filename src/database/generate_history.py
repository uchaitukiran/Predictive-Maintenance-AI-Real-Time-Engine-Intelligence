import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.db import SessionLocal
from src.database.models import Prediction

def generate_balanced_history():
    db = SessionLocal()
    try:
        # -----------------------------------------------------
        # STEP 1: CLEAN THE TABLE (Remove zeros and old data)
        # -----------------------------------------------------
        print("🗑️ Cleaning old predictions...")
        deleted = db.query(Prediction).delete()
        db.commit()
        print(f"Deleted {deleted} old rows.")
        
        new_rows = []
        base_time = datetime.now() - timedelta(hours=5)
        
        print("⚙️ Generating New Data: 300 GOOD, 300 WARNING, 200 CRITICAL")

        # --- Generate 300 GOOD Rows ---
        for i in range(300):
            row = Prediction(
                state="GOOD",
                rul=random.uniform(120, 200),
                temperature=random.uniform(500, 700),
                pressure=random.uniform(400, 550),
                vibration=random.uniform(1000, 1200),
                timestamp=base_time + timedelta(seconds=i*10)
            )
            new_rows.append(row)

        # --- Generate 300 WARNING Rows ---
        for i in range(300):
            row = Prediction(
                state="WARNING",
                rul=random.uniform(30, 99),
                temperature=random.uniform(750, 950),
                pressure=random.uniform(550, 700),
                vibration=random.uniform(1200, 1400),
                timestamp=base_time + timedelta(seconds=(300+i)*10)
            )
            new_rows.append(row)

        # --- Generate 200 CRITICAL Rows ---
        for i in range(200):
            row = Prediction(
                state="CRITICAL",
                rul=random.uniform(0, 29),
                temperature=random.uniform(1000, 1200),
                pressure=random.uniform(750, 900),
                vibration=random.uniform(1450, 1600),
                timestamp=base_time + timedelta(seconds=(600+i)*10)
            )
            new_rows.append(row)

        db.bulk_save_objects(new_rows)
        db.commit()
        print("✅ SUCCESS: Database is now clean and filled with 800 rows.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_balanced_history()