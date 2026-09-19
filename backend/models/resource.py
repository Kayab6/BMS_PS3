from sqlalchemy import Integer, String

from backend.database import db


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(Integer, primary_key=True)
    resource_type = db.Column(String(60), nullable=False)
    name = db.Column(String(120), nullable=False)
    department = db.Column(String(80), nullable=False)
    total_quantity = db.Column(Integer, nullable=False, default=0)
    available_quantity = db.Column(Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "name": self.name,
            "department": self.department,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity,
        }
