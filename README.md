# MEDFLOW

MEDFLOW is a lightweight hospital operations simulation and demo backend built for a hackathon prototype. It combines a Flask API, SQLite database, queue scheduler, resource manager, simulation loop, ML waiting-time predictor, and a Hugging Face-powered operational explainer with a safe rule-based fallback.

## Architecture

```text
Frontend / dashboard
   ↓
Flask API
   ↓
Scheduler + Priority Engine
   ↓
Resource Manager
   ↓
Simulation Engine
   ↓
SQLite database
   ↓
Metrics / queue / patient state
   ↓
ML waiting-time prediction
   ↓
AI operational explanation
   ↓
Fallback explanation
```

## Install

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Initialize database

The app initializes its SQLite tables and sample data automatically on first launch.

```bash
python app.py
```

## Run the Flask app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Train the ML model

```bash
python ml/train.py
```

This creates:

```text
ml/dataset.csv
ml/model.pkl
ml/department_encoder.pkl
```

## Hugging Face configuration

Create a `.env` file from `.env.example` and fill in your tokens if you want to use Hugging Face:

```bash
copy .env.example .env
```

Example:

```env
HF_TOKEN=
HF_MODEL=
```

If the token is missing or the API fails, the app automatically falls back to a rule-based explanation so the dashboard keeps working.

## API endpoints

- `GET /api/health`
- `GET /api/patients`
- `GET /api/resources`
- `GET /api/queue`
- `GET /api/metrics`
- `POST /api/simulation/start`
- `GET /api/simulation/status`
- `POST /api/ml/predict-wait`
- `POST /api/ai/explain`

## Example requests

```bash
curl http://127.0.0.1:5000/api/health
curl http://127.0.0.1:5000/api/patients
curl http://127.0.0.1:5000/api/metrics
curl -X POST http://127.0.0.1:5000/api/ml/predict-wait -H "Content-Type: application/json" -d "{\"urgency\":4,\"queue_length\":10,\"icu_availability\":2,\"bed_availability\":4,\"doctor_availability\":3,\"nurse_availability\":5,\"treatment_duration\":30,\"department\":\"Emergency\"}"
curl -X POST http://127.0.0.1:5000/api/ai/explain -H "Content-Type: application/json" -d "{\"waiting_patients\":18,\"average_waiting_time\":42,\"beds_available\":3,\"doctors_available\":2,\"nurses_available\":4,\"icu_available\":1,\"blood_units\":8,\"medicine_stock\":64,\"highest_queue_department\":\"Emergency\"}"
```

## Notes

- The prototype intentionally keeps the logic readable and easy to demo.
- The app avoids overengineering and reuses the existing scheduling, resource, and simulation modules rather than creating duplicate systems.
- The AI layer is operational only: it explains queue pressure and resource bottlenecks without making clinical decisions.

```text
Priority =
0.60 × Urgency
+
0.20 × Waiting Time
+
0.10 × Department
+
0.10 × Resource Feasibility
```

Weights are configurable.

---

# Scheduling Strategies

### FCFS

Processes patients according to arrival time.

### Urgency Only

Processes patients based primarily on urgency.

### MEDFLOW

Combines:

* urgency
* waiting time
* department priority
* resource feasibility

---

# Inventory

MEDFLOW tracks:

### Blood

```text
A+
A-
B+
B-
AB+
AB-
O+
O-
```

### Medicines

Tracks quantity and minimum stock threshold.

### Equipment

Tracks reusable and consumable medical equipment.

Examples:

```text
Scissors
Clamps
Forceps
Syringes
Monitors
Ventilators
```

---

# Machine Learning

The simulator generates synthetic operational data.

Features include:

```text
urgency
department
queue_length
ICU availability
bed availability
doctor availability
nurse availability
treatment duration
arrival hour
```

The ML model predicts:

```text
patient waiting time
```

The initial model is a Random Forest Regressor.

---

# Hugging Face AI

MEDFLOW uses Hugging Face as an operational explanation layer.

The model receives aggregated metrics such as:

```json
{
  "icu_utilization": 94,
  "average_wait": 24,
  "patients_waiting": 12,
  "critical_patients": 3,
  "medicine_shortages": 2,
  "blood_shortages": 1
}
```

It generates an operational summary.

The AI does not:

* Diagnose patients
* Select medical treatments
* Override resource constraints
* Make clinical decisions

---

# Scenarios

MEDFLOW supports:

### Normal Operation

Standard patient arrival pattern.

### Emergency Surge

Sudden increase in patient arrivals.

### Staff Shortage

Reduced doctor/nurse availability.

### Resource Failure

A resource becomes unavailable.

### Inventory Shortage

Medicine, blood or equipment availability decreases.

---

# Dashboard

The dashboard displays:

* Patients served
* Patients waiting
* Critical patients
* Average waiting time
* ICU utilization
* Overall utilization
* Resource availability
* Inventory
* Alerts
* Queue
* Strategy comparison
* ML prediction
* AI operational insight

---

# Project Structure

```text
MEDFLOW/
├── app.py
├── backend/
├── scheduling/
├── simulation/
├── optimization/
├── resources/
├── ml/
├── ai/
├── metrics/
├── templates/
├── static/
├── tests/
├── requirements.txt
├── PRD.md
└── IMPLEMENTATION.md
```

---

# Team Workflow

Each member works on a separate branch.

```bash
git checkout -b feature/<name>
```

Commit frequently:

```bash
git add .
git commit -m "Implement <feature>"
git push
```

Create a Pull Request into `main`.

---

# Disclaimer

MEDFLOW is a simulated hospital operations system created for educational and hackathon purposes.

It does not provide clinical advice or real-world medical decision-making.

---

# Hackathon Demo

The recommended demonstration:

```text
1. Start simulation

2. Show patient arrivals

3. Show priority queue

4. Show resource allocation

5. Trigger emergency surge

6. Show ICU bottleneck

7. Show medicine/blood shortage

8. Compare scheduling strategies

9. Show ML waiting-time prediction

10. Show Hugging Face operational insight

11. Show final dashboard metrics
```

The central idea:

> MEDFLOW does not simply ask "Who is next?"

It asks:

> "Who should be prioritized while respecting urgency, waiting time, department policy, available capacity, staff, equipment and inventory?"
