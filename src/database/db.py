from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# -----------------------------------------------------
# LOGIC: Check if running on Render (Cloud) or Local (PC)
# -----------------------------------------------------

# 1. Try to get the URL from Environment Variables (Render sets this automatically)
database_url = os.environ.get('DATABASE_URL')

# 2. If it's not found, we are on Local PC. Use your local settings.
if not database_url:
    # KEEP YOUR LOCAL SETTINGS HERE
    database_url = "postgresql://postgres:admin@localhost:5432/engine_health_db"

# Create Engine using the variable we decided above
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models so Base creates the tables
# Note: Ensure this import doesn't cause circular errors in your project structure
from . import models

# This command creates the tables inside PostgreSQL
Base.metadata.create_all(bind=engine)