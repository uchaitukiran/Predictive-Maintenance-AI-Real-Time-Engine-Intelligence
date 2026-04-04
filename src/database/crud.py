from sqlalchemy.orm import Session
from .models import Prediction

def create_prediction(db: Session, state: str, rul: float, temp: float, press: float, vib: float):
    db_pred = Prediction(state=state, rul=rul, temperature=temp, pressure=press, vibration=vib)
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred