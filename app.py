import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from ai.explainer import explain_metrics
from backend.database import (
    BloodInventory,
    EquipmentInventory,
    MedicineInventory,
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
from config import DB_PATH
from resources.manager import ResourceManager
from scheduling.priority_queue import HospitalPriorityQueue
from scheduling.scheduler import Scheduler
from scheduling.strategies import MEDFLOW
from simulation.engine import run_simulation

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
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
        arrival_val = 0.0
        if isinstance(patient.arrival_time, (int, float)):
            arrival_val = float(patient.arrival_time)
        elif isinstance(patient.arrival_time, str):
            try:
                arrival_val = float(patient.arrival_time)
            except ValueError:
                arrival_val = 0.0

        patient_score = MEDFLOW().score_patient(
            {
                "id": patient.id,
                "patient_id": str(patient.id),
                "arrival_time": arrival_val,
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
                "arrival_time": arrival_val,
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
@app.route("/dashboard")
def index():
    return render_template("index.html")


@app.route("/analytics")
@app.route("/reports")
def page_analytics():
    return render_template("analytics.html")


@app.route("/patients")
def page_patients():
    return render_template("patients.html")


@app.route("/scheduling")
def page_scheduling():
    return render_template("index.html")


@app.route("/simulation")
def page_simulation():
    return render_template("index.html")


@app.route("/resources")
def page_resources():
    return render_template("index.html")


@app.route("/ai-insights")
def page_ai_insights():
    return render_template("index.html")


@app.route("/alerts")
def page_alerts():
    return render_template("index.html")


@app.route("/inventory")
def page_inventory():
    return render_template("index.html")


@app.route("/queue")
def page_queue():
    return render_template("index.html")


@app.route("/health")
@app.route("/api/health")
def api_health():
    try:
        db.session.execute(db.select(Patient).limit(1)).first()
        from ml.predict import MODEL_PATH, ENCODER_PATH
        prediction_status = "ok" if MODEL_PATH.exists() and ENCODER_PATH.exists() else "not_ready"
        return jsonify({"status": "ok", "backend": "ok", "database": "ok", "prediction": prediction_status})
    except Exception as exc:
        app.logger.exception("Health check failed")
        return jsonify({"status": "error", "backend": "ok", "database": "error", "error": str(exc)}), 503


@app.route("/api/patients")
def api_patients():
    patients = get_patient_payloads()
    return jsonify(patients)


@app.route("/api/resources")
def api_resources():
    base = get_resource_summary()
    res = {}
    for key, values in base.items():
        total = values["total"]
        available = values["available"]
        allocated = max(0, total - available)
        utilization = round((allocated / total) * 100, 1) if total else 0
        status = "Critical" if utilization >= 80 else "Moderate" if utilization >= 60 else "Optimal"
        res[key] = {"total": total, "available": available, "allocated": allocated, "utilization_percent": utilization, "status": status}
    res["general_beds"] = res["beds"]
    res["icu_beds"] = res["icu"]
    res["or"] = res["operating_rooms"]
    return jsonify(res)


@app.route("/api/queue")
def api_queue():
    patients = Patient.query.filter_by(status="waiting").order_by(Patient.urgency.desc(), Patient.arrival_time.asc()).all()
    queue = []
    for idx, patient in enumerate(patients, start=1):
        estimated_wait = max(0, int((patient.urgency * 8) + (idx * 5) + (patient.treatment_duration / 2)))
        priority = round(max(1.0, (patient.urgency * 3.5) - (idx * 0.2) + 5.0), 1)
        queue.append(
            {
                "patient_id": patient.id,
                "name": patient.name if hasattr(patient, "name") and patient.name else f"Patient #{patient.id}",
                "department": patient.department,
                "urgency": patient.urgency,
                "queue_position": idx,
                "estimated_waiting_time": estimated_wait,
                "priority": priority,
                "status": patient.status,
            }
        )
    return jsonify(queue)


@app.route("/api/metrics")
def api_metrics():
    metrics = get_customer_metric_summary()
    total_patients = Patient.query.count()
    waiting_patients = Patient.query.filter_by(status="waiting").count()
    served_patients = max(0, total_patients - waiting_patients)
    critical_patients = Patient.query.filter(Patient.urgency >= 4, Patient.status == "waiting").count()
    
    res_summary = get_resource_summary()
    icu_total = res_summary.get("icu", {}).get("total", 8)
    icu_avail = res_summary.get("icu", {}).get("available", 2)
    icu_util = round(((icu_total - icu_avail) / icu_total) * 100, 1) if icu_total else 75.0
    
    beds_tot = res_summary.get("beds", {}).get("total", 20)
    beds_av = res_summary.get("beds", {}).get("available", 5)
    beds_util = ((beds_tot - beds_av) / beds_tot) if beds_tot else 0.5
    
    doc_tot = res_summary.get("doctors", {}).get("total", 10)
    doc_av = res_summary.get("doctors", {}).get("available", 3)
    doc_util = ((doc_tot - doc_av) / doc_tot) if doc_tot else 0.5
    
    overall_util = round((beds_util * 0.4 + (icu_util / 100.0) * 0.3 + doc_util * 0.3) * 100, 1)

    metrics.update({
        "patients_served": served_patients,
        "patients_waiting": waiting_patients,
        "critical_patients": critical_patients,
        "icu_utilization": icu_util,
        "overall_resource_utilization": overall_util,
    })
    return jsonify(metrics)


@app.route("/api/blood-bank")
def api_blood_bank():
    records = BloodInventory.query.all()
    if records:
        return jsonify({r.blood_group: r.units_available for r in records})
    groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    return jsonify({g: 12 for g in groups})


@app.route("/api/medicines")
def api_medicines():
    medicines = MedicineInventory.query.all()
    result = []
    for m in medicines:
        status = "NORMAL"
        if m.quantity == 0:
            status = "OUT OF STOCK"
        elif m.quantity < m.minimum_required * 0.5:
            status = "CRITICAL"
        elif m.quantity < m.minimum_required:
            status = "LOW"
        result.append({
            "id": m.id,
            "medicine_name": m.medicine_name,
            "quantity": m.quantity,
            "minimum_required": m.minimum_required,
            "status": status,
        })
    return jsonify(result)


@app.route("/api/equipment")
def api_equipment():
    equipments = EquipmentInventory.query.all()
    result = []
    for eq in equipments:
        in_use = max(0, eq.total_quantity - eq.available_quantity)
        result.append({
            "id": eq.id,
            "equipment_name": eq.equipment_name,
            "available_quantity": eq.available_quantity,
            "total_quantity": eq.total_quantity,
            "in_use": in_use,
        })
    return jsonify(result)


@app.route("/api/alerts")
def api_alerts():
    alerts = []
    res_summary = get_resource_summary()
    icu_avail = res_summary.get("icu", {}).get("available", 2)
    icu_total = res_summary.get("icu", {}).get("total", 8)
    if icu_avail <= 2:
        alerts.append({
            "type": "critical",
            "title": "ICU Capacity Critical",
            "department": "ICU",
            "message": f"ICU available beds down to {icu_avail}/{icu_total}. Immediate triage diversion advised.",
            "time": "Just now",
        })
    
    doc_avail = res_summary.get("doctors", {}).get("available", 3)
    nurse_avail = res_summary.get("nurses", {}).get("available", 6)
    if doc_avail <= 3 or nurse_avail <= 6:
        alerts.append({
            "type": "warning",
            "title": "Clinical Staff Shortage",
            "department": "Hospital-wide",
            "message": f"Doctor on-duty coverage ({doc_avail}) or nurse coverage ({nurse_avail}) below standard buffer.",
            "time": "3m ago",
        })

    low_blood = BloodInventory.query.filter(BloodInventory.units_available < 6).all()
    if low_blood:
        types_str = ", ".join(b.blood_group for b in low_blood[:3])
        alerts.append({
            "type": "critical" if any(b.units_available < 3 for b in low_blood) else "warning",
            "title": "Blood Bank Shortage",
            "department": "Blood Bank",
            "message": f"Units low for blood group(s): {types_str}.",
            "time": "10m ago",
        })

    low_meds = MedicineInventory.query.filter(MedicineInventory.quantity <= MedicineInventory.minimum_required).all()
    if low_meds:
        med_names = ", ".join(m.medicine_name for m in low_meds[:2])
        alerts.append({
            "type": "warning",
            "title": "Medication Threshold Alert",
            "department": "Pharmacy",
            "message": f"Stock under minimum buffer for: {med_names}.",
            "time": "15m ago",
        })

    waiting_count = Patient.query.filter_by(status="waiting").count()
    if waiting_count > 15:
        alerts.append({
            "type": "critical",
            "title": "Emergency Queue Surge",
            "department": "Emergency",
            "message": f"Patient queue volume high with {waiting_count} active waiting patients.",
            "time": "Just now",
        })
    elif not alerts:
        alerts.append({
            "type": "info",
            "title": "Operations Normal",
            "department": "Hospital-wide",
            "message": "All clinical departments and resource levels within standard parameters.",
            "time": "Live",
        })
    return jsonify(alerts)


@app.route("/api/strategies/compare")
def api_strategies_compare():
    patients = Patient.query.filter_by(status="waiting").all()
    resource_summary = get_resource_summary()
    total_capacity = sum(item["total"] for item in resource_summary.values())
    available_capacity = sum(item["available"] for item in resource_summary.values())
    utilization = round(((total_capacity - available_capacity) / total_capacity) * 100, 1) if total_capacity else 0

    def summarize(ordered_patients, name):
        waits = []
        critical_waits = []
        elapsed = 0
        for patient in ordered_patients:
            waits.append(elapsed)
            if patient.urgency >= 4:
                critical_waits.append(elapsed)
            elapsed += max(1, patient.treatment_duration)
        return {
            "name": name,
            "avg_wait_time": round(sum(waits) / len(waits), 1) if waits else 0,
            "critical_wait_time": round(sum(critical_waits) / len(critical_waits), 1) if critical_waits else 0,
            "patients_served": len(ordered_patients),
            "resource_utilization": utilization,
            "bottlenecks": sum(1 for item in resource_summary.values() if item["available"] == 0),
        }

    comparison = {
        "FCFS": summarize(sorted(patients, key=lambda item: item.arrival_time), "First-Come First-Served"),
        "URGENCY_ONLY": summarize(sorted(patients, key=lambda item: (-item.urgency, item.arrival_time)), "Urgency-Only Triage"),
        "MEDFLOW": summarize(sorted(patients, key=lambda item: (-item.urgency, item.treatment_duration, item.arrival_time)), "MEDFLOW (Dynamic Optimization)"),
    }
    return jsonify(comparison)


@app.route("/api/simulation/start", methods=["POST"])
def api_simulation_start():
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario_type") or data.get("scenario") or "normal"
    try:
        run_simulation(scenario)
        run_scheduler_integration()

        simulation_run = SimulationRun(
            start_time=datetime.utcnow().isoformat(),
            end_time=datetime.utcnow().isoformat(),
            status="completed",
        )
        db.session.add(simulation_run)
        db.session.commit()

        SIMULATION_STATE["simulation_id"] = simulation_run.id
        SIMULATION_STATE["status"] = "completed"
        SIMULATION_STATE["time"] = 0
        SIMULATION_STATE["scenario"] = scenario
        SIMULATION_STATE["metrics"] = get_customer_metric_summary()

        return jsonify({"success": True, "simulation_id": simulation_run.id, "scenario": scenario, "message": "Simulation started"})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/simulation/reset", methods=["POST"])
def api_simulation_reset():
    try:
        patients = Patient.query.all()
        for p in patients:
            p.status = "waiting"
        db.session.commit()

        SIMULATION_STATE["simulation_id"] = None
        SIMULATION_STATE["status"] = "idle"
        SIMULATION_STATE["time"] = 0
        SIMULATION_STATE["metrics"] = get_customer_metric_summary()

        return jsonify({"success": True, "message": "Simulation reset successfully"})
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
            "scenario": SIMULATION_STATE.get("scenario", "normal"),
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
