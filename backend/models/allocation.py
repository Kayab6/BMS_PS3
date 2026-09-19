from sqlalchemy import Float, Integer, String

from backend.database import db


class Allocation(db.Model):
    __tablename__ = "allocations"

    id = db.Column(Integer, primary_key=True)
    patient_id = db.Column(Integer, nullable=False)
    resource_id = db.Column(Integer, nullable=False)
    allocation_time = db.Column(String(50), nullable=False)
    release_time = db.Column(String(50), nullable=True)
    status = db.Column(String(40), nullable=False, default="active")
