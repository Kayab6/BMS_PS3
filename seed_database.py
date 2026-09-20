"""Create the deterministic MEDFLOW demo dataset without deleting existing data."""

from datetime import datetime, timedelta

from app import app
from backend.database import Patient, db, initialize_database


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialize_database()
        now = datetime.utcnow()
        for index, patient in enumerate(Patient.query.order_by(Patient.id.asc()).all()):
            patient.arrival_time = (now - timedelta(minutes=(index % 20) * 3)).isoformat(timespec="seconds")
            patient.status = "waiting"
        db.session.commit()
        print("MEDFLOW demo database is ready.")