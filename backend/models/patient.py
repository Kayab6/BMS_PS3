from sqlalchemy import Integer, String

from backend.database import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    age = db.Column(Integer, nullable=False)
    department = db.Column(String(80), nullable=False)
    urgency = db.Column(Integer, nullable=False, default=1)
    arrival_time = db.Column(String(50), nullable=False)
    treatment_duration = db.Column(Integer, nullable=False, default=30)
    status = db.Column(String(40), nullable=False, default="waiting")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "department": self.department,
            "urgency": self.urgency,
            "arrival_time": self.arrival_time,
            "treatment_duration": self.treatment_duration,
            "status": self.status,
        }
