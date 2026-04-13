from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class EngineSensorData(Base):
    __tablename__ = 'engine_sensor_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    op_setting_1 = Column(Float)
    op_setting_2 = Column(Float)
    op_setting_3 = Column(Float)
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

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(50))
    rul = Column(Float)
    temperature = Column(Float)
    pressure = Column(Float)
    vibration = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MaintenanceReport(Base):
    __tablename__ = 'maintenance_reports'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    engine_state = Column(String(50))
    rul = Column(Float)
    report_text = Column(Text)
    sensor_summary = Column(String(255))
    is_deleted = Column(Integer, default=0)