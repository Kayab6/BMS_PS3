# MEDFLOW

**MEDFLOW** is a lightweight hospital operations simulation platform built for hackathons and educational demonstrations.

It simulates patient flow through a hospital while considering **urgency, waiting time, department priority, staff availability, beds, ICU capacity, equipment, and inventory**. It combines a Flask backend, SQLite database, scheduling engine, resource manager, simulation engine, machine-learning wait-time predictor, and an AI-powered operational explanation layer.

> **MEDFLOW is a hospital operations simulation system. It is not a clinical decision-support system and does not provide medical advice.**

---

## Demo Video



https://github.com/user-attachments/assets/00d490a8-9efc-41a4-91c6-1d56c54240a6





## What MEDFLOW Does

Hospitals constantly have to make operational decisions such as:

* Which patient should be processed next?
* How should limited beds and staff be allocated?
* Where are the current bottlenecks?
* How will an emergency surge affect waiting times?
* What happens if doctors or nurses become unavailable?
* What happens when blood, medicine, or equipment inventory becomes constrained?
* How do different scheduling strategies affect patient flow?

MEDFLOW provides a simulated environment for exploring these questions.

Instead of using a simple **First-Come, First-Served (FCFS)** queue, MEDFLOW uses a configurable priority score that considers multiple operational factors.

```text
Priority Score =
    0.60 × Urgency
  + 0.20 × Waiting Time
  + 0.10 × Department Priority
  + 0.10 × Resource Feasibility
```

The weights are configurable and can be adjusted for different simulation scenarios.

---

# Architecture

```text
                    ┌─────────────────────┐
                    │ Frontend / Dashboard │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Flask API       │
                    └──────────┬──────────┘
                               │
                               ▼
                 ┌───────────────────────────┐
                 │ Scheduler + Priority      │
                 │ Engine                    │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │    Resource Manager       │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │    Simulation Engine      │
                 └────────────┬──────────────┘
                              │
                              ▼
                 ┌───────────────────────────┐
                 │      SQLite Database      │
                 └────────────┬──────────────┘
                              │
                ┌─────────────┴──────────────┐
                ▼                            ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ ML Wait-Time    │          │ Metrics / Queue │
       │ Predictor       │          │ / Patient State │
       └────────┬────────┘          └─────────────────┘
                │
                ▼
       ┌─────────────────────────┐
       │ AI Operational          │
       │ Explanation Layer       │
       └────────────┬────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │ Rule-Based Fallback     │
       └─────────────────────────┘
```

The AI layer is intentionally separated from the scheduling and resource-management logic. It provides explanations of operational conditions rather than making clinical decisions.

---

# Core Features

## 1. Patient Queue Management

MEDFLOW maintains a simulated patient queue containing information such as:

* Arrival time
* Urgency
* Department
* Treatment duration
* Current waiting time
* Required resources
* Patient status

Patients are continuously processed by the simulation engine according to the selected scheduling strategy.

---

## 2. Scheduling Strategies

MEDFLOW supports multiple strategies for comparison.

### FCFS — First Come, First Served

Patients are processed according to arrival order.

```text
Earlier arrival → Higher priority
```

### Urgency-Based Scheduling

Patients are primarily prioritized according to urgency.

```text
Higher urgency → Higher priority
```

### MEDFLOW Strategy

MEDFLOW combines multiple operational factors:

* Patient urgency
* Waiting time
* Department priority
* Resource feasibility

This allows the simulation to demonstrate how a multi-factor scheduling strategy behaves under different hospital conditions.

---

# 3. Resource Management

MEDFLOW tracks operational resources required during simulation.

### Hospital Capacity

* Beds
* ICU beds
* Doctors
* Nurses

### Equipment

Examples include:

* Scissors
* Clamps
* Forceps
* Syringes
* Patient monitors
* Ventilators

The resource manager considers availability when determining whether a patient can be processed.

---

# 4. Inventory Management

MEDFLOW simulates hospital inventory.

### Blood Inventory

The system tracks the following blood groups:

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

The system tracks:

* Current quantity
* Minimum stock threshold
* Stock availability
* Potential shortages

### Equipment

Equipment can be represented as reusable or consumable resources depending on the simulation configuration.

Inventory constraints can be introduced during scenarios to demonstrate their effect on hospital operations.

---

# 5. Hospital Simulation

The simulation engine models changing hospital conditions over time.

MEDFLOW supports several scenarios.

### Normal Operation

Represents a relatively stable patient arrival pattern and resource availability.

### Emergency Surge

Simulates a sudden increase in patient arrivals.

This can create:

```text
More arrivals
      ↓
Longer queues
      ↓
Higher resource utilization
      ↓
Increased waiting times
```

### Staff Shortage

Reduces the availability of doctors and/or nurses.

### Resource Failure

Temporarily removes a resource from service.

### Inventory Shortage

Reduces the availability of medicines, blood, or equipment.

These scenarios allow the same scheduling system to be tested under different operational conditions.

---

# 6. Machine Learning Wait-Time Prediction

MEDFLOW includes a machine-learning component for estimating patient waiting time.

The simulator can generate synthetic operational data using features such as:

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

The model predicts:

```text
Estimated Patient Waiting Time
```

The initial implementation uses a **Random Forest Regressor**.

## Training

Run:

```bash
python ml/train.py
```

This generates the model artifacts used by the application:

```text
ml/dataset.csv
ml/model.pkl
ml/department_encoder.pkl
```

### Important

The training data is **synthetically generated for simulation purposes**. The model should therefore be interpreted as a demonstration of operational prediction rather than a validated real-world hospital forecasting model.

---

# 7. AI Operational Explanation

MEDFLOW includes a Hugging Face-powered explanation layer.

The AI receives aggregated operational information such as:

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

It generates a concise operational explanation describing factors such as:

* Queue pressure
* Resource bottlenecks
* ICU utilization
* Inventory shortages
* Waiting-time trends

### Safety Boundary

The AI layer does **not**:

* Diagnose patients
* Recommend treatments
* Select medications
* Override resource constraints
* Make clinical decisions
* Replace medical professionals

If Hugging Face is unavailable or no token is configured, MEDFLOW uses a **rule-based fallback** so the operational dashboard can continue functioning.

---

# API

The Flask backend exposes the following endpoints:

| Method | Endpoint                 | Purpose                             |
| ------ | ------------------------ | ----------------------------------- |
| GET    | `/api/health`            | Check application health            |
| GET    | `/api/patients`          | Retrieve simulated patients         |
| GET    | `/api/resources`         | Retrieve resource availability      |
| GET    | `/api/queue`             | Retrieve current queue              |
| GET    | `/api/metrics`           | Retrieve operational metrics        |
| POST   | `/api/simulation/start`  | Start the simulation                |
| GET    | `/api/simulation/status` | Retrieve simulation status          |
| POST   | `/api/ml/predict-wait`   | Predict patient waiting time        |
| POST   | `/api/ai/explain`        | Generate an operational explanation |

### Example Requests

Check application health:

```bash
curl http://127.0.0.1:5000/api/health
```

Retrieve patients:

```bash
curl http://127.0.0.1:5000/api/patients
```

Retrieve metrics:

```bash
curl http://127.0.0.1:5000/api/metrics
```

Predict waiting time:

```bash
curl -X POST http://127.0.0.1:5000/api/ml/predict-wait ^
  -H "Content-Type: application/json" ^
  -d "{\"urgency\":4,\"queue_length\":10,\"icu_availability\":2,\"bed_availability\":4,\"doctor_availability\":3,\"nurse_availability\":5,\"treatment_duration\":30,\"department\":\"Emergency\"}"
```

Generate an operational explanation:

```bash
curl -X POST http://127.0.0.1:5000/api/ai/explain ^
  -H "Content-Type: application/json" ^
  -d "{\"waiting_patients\":18,\"average_waiting_time\":42,\"beds_available\":3,\"doctors_available\":2,\"nurses_available\":4,\"icu_available\":1,\"blood_units\":8,\"medicine_stock\":64,\"highest_queue_department\":\"Emergency\"}"
```

> On Linux/macOS, replace the `^` line-continuation characters with `\`, or place the command on a single line.

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Kayab6/BMS_PS3_MedFlow.git
cd BMS_PS3_MedFlow
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

MEDFLOW can optionally use Hugging Face for AI-generated operational explanations.

Create a `.env` file from the provided example:

### Windows

```bash
copy .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

Then configure:

```env
HF_TOKEN=your_token_here
HF_MODEL=your_model_here
```

The Hugging Face integration is optional.

If the token is missing or the external API is unavailable, MEDFLOW automatically uses its rule-based fallback.

**Do not commit `.env` or API tokens to GitHub.**

---

# Running MEDFLOW

The database is initialized automatically when the application starts.

Run:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

# Dashboard

The dashboard provides a real-time view of the simulated hospital environment.

It can display:

* Patients served
* Patients waiting
* Critical patients
* Average waiting time
* ICU utilization
* Overall resource utilization
* Bed availability
* Staff availability
* Inventory levels
* Alerts
* Current queue
* Scheduling strategy comparison
* ML waiting-time prediction
* AI-generated operational insights

---

# Project Structure

```text
MEDFLOW/
│
├── app.py
├── requirements.txt
├── README.md
├── PRD.md
├── IMPLEMENTATION.md
│
├── backend/
│   └── ...
│
├── scheduling/
│   └── ...
│
├── simulation/
│   └── ...
│
├── optimization/
│   └── ...
│
├── resources/
│   └── ...
│
├── ml/
│   ├── train.py
│   ├── dataset.csv
│   ├── model.pkl
│   └── department_encoder.pkl
│
├── ai/
│   └── ...
│
├── metrics/
│   └── ...
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
└── tests/
    └── ...
```

---

# Example Simulation Flow

A typical simulation can be demonstrated as:

```text
Patient Arrivals
       ↓
Patient Queue
       ↓
Priority Calculation
       ↓
Resource Availability Check
       ↓
Patient Allocation
       ↓
Treatment Simulation
       ↓
Resource Release
       ↓
Metrics Update
       ↓
ML Waiting-Time Prediction
       ↓
AI Operational Explanation
```

---
