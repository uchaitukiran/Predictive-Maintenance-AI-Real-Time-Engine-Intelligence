from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base

# TABLE 1: Stores the Live Sensor Data (Inputs)
class EngineSensorData(Base):
    __tablename__ = "engine_sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cycle = Column(Integer, index=True)
    
    # Operational Settings
    op_setting_1 = Column(Float)
    op_setting_2 = Column(Float)
    op_setting_3 = Column(Float)
    
    # Sensors (Add all sensors your model needs)
    sensor_2 = Column(Float)
    sensor_3 = Column(Float)
    sensor_4 = Column(Float)
    sensor_7 = Column(Float)
    sensor_8 = Column(Float)
    sensor_9 = Column(Float)
    sensor_11 = Column(Float)
    sensor_12 = Column(Float)
    sensor_13 = Column(Float)
    sensor_14 = Column(Float)
    sensor_15 = Column(Float)
    sensor_17 = Column(Float)
    sensor_20 = Column(Float)
    sensor_21 = Column(Float)
    
    is_processed = Column(Boolean, default=False) # To track simulation progress

# TABLE 2: Stores the Model Predictions (Outputs)
class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String)
    rul = Column(Float)
    temperature = Column(Float) # You can map sensor_2 here if needed
    pressure = Column(Float)
    vibration = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())