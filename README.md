# MEDFLOW

## Prioritize Patients. Optimize Resources.

MEDFLOW is a hospital resource management simulator designed to simulate patient flow and intelligently allocate constrained hospital resources.

The system combines:

* Priority-based scheduling
* Discrete-event simulation
* Resource allocation
* Inventory management
* Optimization
* Machine learning
* Hugging Face AI explanations
* Interactive operational dashboard

---

# Problem

Hospitals operate with limited resources while patients arrive continuously with different urgency levels and resource requirements.

MEDFLOW simulates this environment and attempts to reduce waiting time while respecting resource and inventory constraints.

---

# Key Features

## Patient Management

* Simulated patient arrivals
* Urgency levels
* Department classification
* Treatment duration
* Dynamic patient queue
* Waiting-time tracking

## Resource Management

* General beds
* ICU beds
* Doctors
* Nurses
* Operating rooms
* Ambulances

## Inventory

* Blood bank
* Medicines
* Medical equipment
* Consumable equipment

## Scheduling

* FCFS
* Urgency-only
* MEDFLOW hybrid scheduling

## Simulation

* Normal operation
* Emergency patient surge
* Staff shortages
* Resource failures
* Inventory shortages

## Analytics

* Average waiting time
* Maximum waiting time
* Resource utilization
* Queue length
* Throughput
* Bottleneck detection
* Strategy comparison

## Machine Learning

Predicts patient waiting time using operational features.

## Hugging Face AI

Generates natural-language operational explanations from structured hospital metrics.

The AI layer does not make clinical decisions.

---

# Architecture

```text
HTML/CSS/JavaScript
        │
        ↓
      Flask
        │
 ┌──────┼──────────┐
 ↓      ↓          ↓
Queue Simulation Metrics
 │       │
 └───────┼─────────┘
         ↓
 Resource Manager
         │
 ┌───────┼───────────────┐
 ↓       ↓       ↓       ↓
Beds   Staff   Inventory Equipment
         │
         ↓
       SQLite
         │
    ┌────┴────┐
    ↓         ↓
   ML     Hugging Face
```

---

# Technology Stack

| Component       | Technology                      |
| --------------- | ------------------------------- |
| Backend         | Python + Flask                  |
| Database        | SQLite                          |
| ORM             | SQLAlchemy                      |
| Scheduling      | Python heapq                    |
| Optimization    | Google OR-Tools                 |
| Simulation      | Custom discrete-event simulator |
| ML              | Scikit-learn                    |
| AI              | Hugging Face                    |
| Frontend        | HTML/CSS/JavaScript             |
| Charts          | Chart.js                        |
| Version Control | Git/GitHub                      |

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd MEDFLOW
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create:

```text
.env
```

Example:

```text
SECRET_KEY=your-secret-key
HF_TOKEN=your-huggingface-token
```

Never commit `.env`.

Add it to:

```text
.gitignore
```

---

# Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# Simulation Flow

```text
Patient Arrival
      ↓
Department + Urgency
      ↓
Priority Calculation
      ↓
Priority Queue
      ↓
Resource Check
      ↓
Inventory Check
      ↓
Allocation
      ↓
Treatment
      ↓
Resource Release
      ↓
Metrics
      ↓
Dashboard
      ↓
ML Prediction
      ↓
AI Operational Explanation
```

---

# Priority Calculation

MEDFLOW considers:

```text
Urgency
Waiting Time
Department Priority
Resource Feasibility
```

Example:

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
