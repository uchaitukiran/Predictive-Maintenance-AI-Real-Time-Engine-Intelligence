from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# -----------------------------------------------------
# PostgreSQL Connection
# Format: postgresql://<user>:<password>@<host>:<port>/<db_name>
# Change 'admin' to the password you set during installation!
# -----------------------------------------------------
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/engine_health_db"

# Create Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # Good practice for Postgres: checks if connection is alive
    pool_size=10,       # Allows multiple users at once
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models so Base creates the tables
from . import models

# This command creates the tables inside PostgreSQL
Base.metadata.create_all(bind=engine)