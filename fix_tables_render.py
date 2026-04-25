import os
import sys
from sqlalchemy import create_engine

# --- CONFIGURATION ---
# REPLACE THIS WITH YOUR EXTERNAL DATABASE URL
RENDER_URL = "postgresql://engine_health_db_user:tG3dHmaOtqqF2YfN3z4BQvibiZO23oTl@dpg-d7lg3lm7r5hc739m1230-a.singapore-postgres.render.com/engine_health_db"

# Setup path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def create_tables():
    print("🔄 Connecting to Render Database...")
    try:
        # Import Base and ALL Models
        from src.database.db import Base
        from src.database.models import EngineSensorData, Prediction, MaintenanceReport
        
        # Connect
        engine = create_engine(RENDER_URL)
        
        # Create Tables
        print("🚀 Creating missing tables (Predictions, Reports)...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ SUCCESS: All tables created in Render Cloud!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tables()