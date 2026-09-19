from sqlalchemy import DateTime, Integer, String

from backend.database import db


class SimulationRun(db.Model):
    __tablename__ = "simulation_runs"

    id = db.Column(Integer, primary_key=True)
    start_time = db.Column(String(50), nullable=False)
    end_time = db.Column(String(50), nullable=True)
    status = db.Column(String(40), nullable=False, default="running")

    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
        }
