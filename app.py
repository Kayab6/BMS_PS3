import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from ai.explainer import explain_metrics
from backend.database import (
    Patient,
    Resource,
    SimulationRun,
    db,
    get_customer_metric_summary,
    get_patient_payloads,
    get_resource_summary,
    initialize_database,
)
from ml.predict import predict_wait_time
from resources.manager import ResourceManager
from scheduling.priority_queue import HospitalPriorityQueue
from scheduling.scheduler import Scheduler
from scheduling.strategies import MEDFLOW
from simulation.engine import run_simulation

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///medflow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

SIMULATION_STATE = {"simulation_id": None, "status": "idle", "time": 0, "metrics": {}}


class SchedulerResourceAdapter:
    def __init__(self):
        self.manager = ResourceManager()

    def can_allocate(self, patient):
        needs_icu = bool(patient.get("needs_icu"))
        needs_doctor = bool(patient.get("needs_doctor", True))
        needs_medicine = bool(patient.get("needs_medicine"))

        if needs_icu and not self.manager.is_available("hospital", "icu"):
            return False
        if not needs_icu and not self.manager.is_available("hospital", "bed"):
            return False
        if needs_doctor and not self.manager.is_available("hospital", "doctor"):
            return False
        if needs_medicine and not self.manager.is_available("medicine", "painkillers"):
            return False
        return True

    def allocate(self, patient):
        needs_icu = bool(patient.get("needs_icu"))
        needs_doctor = bool(patient.get("needs_doctor", True))
        needs_medicine = bool(patient.get("needs_medicine"))

        if needs_icu:
            self.manager.allocate("hospital", "icu")
        else:
            self.manager.allocate("hospital", "bed")

        if needs_doctor:
            self.manager.allocate("hospital", "doctor")
        if needs_medicine:
            self.manager.allocate("medicine", "painkillers")
        return True


def ensure_app_database():
    with app.app_context():
        db.create_all()
        initialize_database()


def run_scheduler_integration():
    patients = Patient.query.filter_by(status="waiting").all()
    if not patients:
        return []

    queue = HospitalPriorityQueue()
    for patient in patients:
        patient_score = MEDFLOW().score_patient(
            {
                "id": patient.id,
                "patient_id": str(patient.id),
                "arrival_time": patient.arrival_time if patient.arrival_time else 0,
                "urgency": patient.urgency,
                "department": patient.department,
                "department_priority": 3,
                "resource_feasibility": 1,
            },
            current_time=0,
        )
        queue.push(
            {
                "id": patient.id,
                "patient_id": str(patient.id),
                "arrival_time": patient.arrival_time if patient.arrival_time else 0,
                "urgency": patient.urgency,
                "department": patient.department,
                "needs_icu": patient.department.lower() == "icu" or patient.urgency >= 4,
                "needs_doctor": True,
                "needs_medicine": patient.urgency >= 3,
            },
            patient_score,
        )

    resource_adapter = SchedulerResourceAdapter()
    scheduler = Scheduler()
    scheduled = scheduler.batch_schedule(queue, resource_adapter, max_allocations=10)

    for patient in scheduled:
        db_patient = Patient.query.get(patient["id"])
        if db_patient:
            db_patient.status = "allocated"
    db.session.commit()
    return scheduled


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.route("/api/patients")
def api_patients():
    patients = get_patient_payloads()
    return jsonify(patients)


@app.route("/api/resources")
def api_resources():
    return jsonify(get_resource_summary())


@app.route("/api/queue")
def api_queue():
    patients = Patient.query.filter_by(status="waiting").order_by(Patient.urgency.desc(), Patient.arrival_time.asc()).all()
    queue = []
    for idx, patient in enumerate(patients, start=1):
        estimated_wait = max(0, int((patient.urgency * 8) + (idx * 5) + (patient.treatment_duration / 2)))
        queue.append(
            {
                "patient_id": patient.id,
                "department": patient.department,
                "urgency": patient.urgency,
                "queue_position": idx,
                "estimated_waiting_time": estimated_wait,
                "status": patient.status,
            }
        )
    return jsonify(queue)


@app.route("/api/metrics")
def api_metrics():
    metrics = get_customer_metric_summary()
    return jsonify(metrics)


@app.route("/api/simulation/start", methods=["POST"])
def api_simulation_start():
    try:
        run_simulation("normal")
        run_scheduler_integration()

        simulation_run = SimulationRun(
            start_time=datetime.utcnow().isoformat(),
            end_time=None,
            status="running",
        )
        db.session.add(simulation_run)
        db.session.commit()

        SIMULATION_STATE["simulation_id"] = simulation_run.id
        SIMULATION_STATE["status"] = "running"
        SIMULATION_STATE["time"] = 0
        SIMULATION_STATE["metrics"] = get_customer_metric_summary()

        return jsonify({"success": True, "simulation_id": simulation_run.id, "message": "Simulation started"})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/simulation/status")
def api_simulation_status():
    if SIMULATION_STATE["simulation_id"] is None:
        latest_run = SimulationRun.query.order_by(SimulationRun.id.desc()).first()
        if latest_run:
            SIMULATION_STATE["simulation_id"] = latest_run.id
            SIMULATION_STATE["status"] = latest_run.status
    return jsonify(
        {
            "simulation_id": SIMULATION_STATE["simulation_id"],
            "status": SIMULATION_STATE["status"],
            "time": SIMULATION_STATE["time"],
            "metrics": get_customer_metric_summary(),
        }
    )


@app.route("/api/ml/predict-wait", methods=["POST"])
def api_predict_wait():
    data = request.get_json(silent=True) or {}
    required_fields = [
        "urgency",
        "queue_length",
        "icu_availability",
        "bed_availability",
        "doctor_availability",
        "nurse_availability",
        "treatment_duration",
        "department",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({"success": False, "error": f"Missing required field: {missing[0]}"}), 400

    try:
        result = predict_wait_time(data)
        return jsonify({"success": True, **result})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/ai/explain", methods=["POST"])
def api_ai_explain():
    metrics = request.get_json(silent=True) or {}
    required_fields = [
        "waiting_patients",
        "average_waiting_time",
        "beds_available",
        "doctors_available",
        "nurses_available",
        "icu_available",
        "blood_units",
        "medicine_stock",
        "highest_queue_department",
    ]
    missing = [field for field in required_fields if field not in metrics]
    if missing:
        return jsonify({"success": False, "error": f"Missing required field: {missing[0]}"}), 400

    try:
        response = explain_metrics(metrics)
        return jsonify(response)
    except Exception as exc:
        fallback = {
            "success": True,
            "source": "fallback",
            "explanation": "Waiting pressure remains high and resource availability is constrained. Immediate operational focus should be on queue reduction and bed staffing.",
        }
        return jsonify(fallback)


ensure_app_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
