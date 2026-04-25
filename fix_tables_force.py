import os
import sys
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
# Added ?sslmode=require to force secure connection
RENDER_URL = "postgresql://engine_health_db_user:tG3dHmaOtqqF2YfN3z4BQvibiZO23oTl@dpg-d7lg3lm7r5hc739m1230-a.singapore-postgres.render.com/engine_health_db?sslmode=require"

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def create_tables_force():
    print("🔄 Connecting to Render Database (Secure Mode)...")

    try:
        engine = create_engine(RENDER_URL)
        
        # We will use RAW SQL to force create the tables
        # This bypasses any SQLAlchemy confusion
        
        with engine.connect() as conn:
            print("🔨 Creating 'predictions' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(50),
                    rul FLOAT,
                    temperature FLOAT,
                    pressure FLOAT,
                    vibration FLOAT,
                    timestamp TIMESTAMP
                );
            """))
            
            print("🔨 Creating 'maintenance_reports' table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS maintenance_reports (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    engine_state VARCHAR(50),
                    rul FLOAT,
                    report_text TEXT,
                    sensor_summary VARCHAR(255),
                    is_deleted INTEGER DEFAULT 0
                );
            """))
            
            conn.commit()
            print("✅ SUCCESS: Tables created via SQL!")

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\n⚠️ TIP: If this fails again, wait 2 minutes and try again. Free databases sometimes sleep.")

if __name__ == "__main__":
    create_tables_force()