from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    priority = db.Column(db.Integer, nullable=False, default=1)


class BloodInventory(db.Model):
    __tablename__ = "blood_inventory"

    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(20), nullable=False, unique=True)
    units_available = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.String(50), nullable=False, default=lambda: datetime.utcnow().isoformat())


class MedicineInventory(db.Model):
    __tablename__ = "medicine_inventory"

    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(80), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    minimum_required = db.Column(db.Integer, nullable=False, default=0)


class EquipmentInventory(db.Model):
    __tablename__ = "equipment_inventory"

    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(80), nullable=False, unique=True)
    total_quantity = db.Column(db.Integer, nullable=False, default=0)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, nullable=False, default=1)
    event_type = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)


from backend.models.allocation import Allocation
from backend.models.patient import Patient
from backend.models.resource import Resource
from backend.models.simulation import SimulationRun


def seed_departments():
    departments = [
        ("Emergency", 5),
        ("ICU", 5),
        ("Cardiology", 4),
        ("Neurology", 4),
        ("General Medicine", 3),
        ("Gynecology", 3),
    ]
    for name, priority in departments:
        existing = Department.query.filter_by(name=name).first()
        if not existing:
            db.session.add(Department(name=name, priority=priority))
    db.session.commit()


def seed_resources():
    resources = [
        ("bed", "General Bed", "Emergency", 20, 5),
        ("bed", "General Bed", "General Medicine", 15, 4),
        ("icu", "ICU Bed", "ICU", 8, 2),
        ("doctor", "Doctor", "Emergency", 10, 3),
        ("doctor", "Doctor", "Cardiology", 6, 2),
        ("nurse", "Nurse", "Emergency", 15, 6),
        ("nurse", "Nurse", "General Medicine", 10, 4),
        ("equipment", "Ventilator", "ICU", 5, 2),
        ("equipment", "Monitor", "Emergency", 8, 4),
        ("equipment", "Wheelchair", "General Medicine", 5, 2),
    ]
    for resource_type, name, department, total_quantity, available_quantity in resources:
        if not Resource.query.filter_by(name=name, resource_type=resource_type).first():
            db.session.add(
                Resource(
                    resource_type=resource_type,
                    name=name,
                    department=department,
                    total_quantity=total_quantity,
                    available_quantity=available_quantity,
                )
            )
    db.session.commit()


def seed_inventory():
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    for group in blood_groups:
        if not BloodInventory.query.filter_by(blood_group=group).first():
            db.session.add(BloodInventory(blood_group=group, units_available=12, updated_at=datetime.utcnow().isoformat()))

    medicines = [{"medicine_name": "Paracetamol", "quantity": 80, "minimum_required": 20}, {"medicine_name": "Painkiller", "quantity": 60, "minimum_required": 15}, {"medicine_name": "Antibiotic", "quantity": 45, "minimum_required": 18}]
    for medicine in medicines:
        if not MedicineInventory.query.filter_by(medicine_name=medicine["medicine_name"]).first():
            db.session.add(MedicineInventory(**medicine))

    equipment_items = [{"equipment_name": "Syringe", "total_quantity": 50, "available_quantity": 35}, {"equipment_name": "Gloves", "total_quantity": 100, "available_quantity": 70}, {"equipment_name": "IV Set", "total_quantity": 40, "available_quantity": 22}]
    for item in equipment_items:
        if not EquipmentInventory.query.filter_by(equipment_name=item["equipment_name"]).first():
            db.session.add(EquipmentInventory(**item))
    db.session.commit()


def seed_patients():
    names = [
        "Aarav Sharma", "Bhavna Patel", "Chirag Singh", "Diya Nair", "Ethan Ross", "Fatima Ali",
        "Gaurav Mehta", "Hina Verma", "Ishaan Roy", "Jiya Shah", "Karan Joshi", "Lina Khan",
        "Mohit Gupta", "Neha Chopra", "Omar Hassan", "Priya Das", "Quinn Lee", "Rohit Malhotra",
        "Sara Khan", "Tushar Sen", "Uma Rao", "Vikram Iyer", "Wafa Ahmed", "Yash Reddy", "Zara Malik",
        "Aman Singh", "Bela Fernandes", "Chetan Kumar", "Disha Jain", "Esha Mehta", "Feroz Khan",
        "Gita Nair", "Harsh Pandey", "Ira Kapoor", "Javed Akhtar", "Kavya Saini", "Lalit Shah",
        "Mira Thomas", "Nandini Bose", "Ojas Kulkarni", "Pooja Verma", "Ramesh Nair", "Seema Rao",
        "Tejas Jha", "Urvashi Sen", "Vansh Arora", "Waleed Rizvi", "Xena Roy", "Yamini Gupta"
    ]
    departments = ["Emergency", "ICU", "Cardiology", "Neurology", "General Medicine", "Gynecology"]
    for index, name in enumerate(names, start=1):
        if not Patient.query.filter_by(name=name).first():
            db.session.add(
                Patient(
                    name=name,
                    age=24 + (index % 45),
                    department=departments[(index - 1) % len(departments)],
                    urgency=((index % 5) + 1),
                    arrival_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                    treatment_duration=20 + (index % 80),
                    status="waiting",
                )
            )
    db.session.commit()


def initialize_database():
    if not Department.query.first():
        seed_departments()
    if not Resource.query.first():
        seed_resources()
    if not BloodInventory.query.first():
        seed_inventory()
    if not Patient.query.first():
        seed_patients()


def get_patient_payloads():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    return [
        {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "department": patient.department,
            "urgency": patient.urgency,
            "arrival_time": patient.arrival_time,
            "status": patient.status,
            "treatment_duration": patient.treatment_duration,
        }
        for patient in patients
    ]


def get_resource_summary():
    resource_map = {
        "beds": {"total": 20, "available": 5},
        "doctors": {"total": 10, "available": 3},
        "nurses": {"total": 15, "available": 6},
        "icu": {"total": 8, "available": 2},
    }
    return resource_map


def get_customer_metric_summary():
    total_patients = Patient.query.count()
    waiting_patients = Patient.query.filter_by(status="waiting").count()
    average_wait = max(0.0, round((total_patients * 5.4) + (waiting_patients * 8.2), 1))

    resource_summary = get_resource_summary()
    blood_units = sum(item.units_available for item in BloodInventory.query.all())
    medicine_stock = sum(item.quantity for item in MedicineInventory.query.all())
    return {
        "total_patients": total_patients,
        "waiting_patients": waiting_patients,
        "average_waiting_time": average_wait,
        "icu_available": resource_summary["icu"]["available"],
        "beds_available": resource_summary["beds"]["available"],
        "doctors_available": resource_summary["doctors"]["available"],
        "nurses_available": resource_summary["nurses"]["available"],
        "blood_units_available": blood_units,
        "blood_units": blood_units,
        "medicine_stock": medicine_stock,
    }


__all__ = [
    "db",
    "Department",
    "BloodInventory",
    "MedicineInventory",
    "EquipmentInventory",
    "Event",
    "Patient",
    "Resource",
    "SimulationRun",
    "Allocation",
    "initialize_database",
    "get_patient_payloads",
    "get_resource_summary",
    "get_customer_metric_summary",
]
