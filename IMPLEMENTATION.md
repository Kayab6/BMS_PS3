# MEDFLOW

## Implementation Guide

**Goal:** Working, deployed prototype within 8 hours.

---

# 1. Final Technology Stack

## Backend

* Python
* Flask
* SQLAlchemy
* SQLite
* REST APIs

## Scheduling

* Python `heapq`
* Custom priority algorithm

## Simulation

* Python discrete-event simulation
* Custom event queue

## Optimization

* Google OR-Tools

## ML

* Pandas
* NumPy
* Scikit-learn
* RandomForestRegressor

## AI

* Hugging Face model/API

## Frontend

* HTML
* CSS
* JavaScript
* Chart.js

## Version Control

* Git
* GitHub

## Deployment

Deploy Flask application to a platform suitable for the team's account and hackathon environment.

---

# 2. Architecture

```text
                    FRONTEND
              HTML + CSS + JS
                     │
                  REST API
                     │
                   FLASK
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    Scheduler    Simulation     Metrics
        │            │
        ↓            ↓
 Resource Manager   Events
        │
 ┌──────┼───────────────┐
 ↓      ↓       ↓       ↓
Beds   Staff   Inventory Equipment
        │
        ↓
     SQLite
        │
 ┌──────┴─────────┐
 ↓                ↓
ML Engine      HF Explainer
```

---

# 3. Project Structure

```text
MEDFLOW/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── PRD.md
├── IMPLEMENTATION.md
│
├── backend/
│   ├── __init__.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── patient.py
│   │   ├── resource.py
│   │   ├── allocation.py
│   │   ├── simulation.py
│   │   ├── blood.py
│   │   ├── medicine.py
│   │   └── equipment.py
│   │
│   └── routes/
│       ├── patients.py
│       ├── resources.py
│       ├── simulation.py
│       ├── metrics.py
│       └── scenarios.py
│
├── scheduling/
│   ├── priority.py
│   ├── priority_queue.py
│   ├── scheduler.py
│   └── strategies.py
│
├── simulation/
│   ├── engine.py
│   ├── events.py
│   └── generator.py
│
├── optimization/
│   ├── model.py
│   ├── constraints.py
│   └── solver.py
│
├── resources/
│   ├── manager.py
│   ├── hospital.py
│   ├── blood_bank.py
│   ├── medicine_inventory.py
│   └── equipment_inventory.py
│
├── ml/
│   ├── features.py
│   ├── train.py
│   ├── predict.py
│   └── model.pkl
│
├── ai/
│   └── explainer.py
│
├── metrics/
│   └── calculator.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       ├── simulation.js
│       └── charts.js
│
└── tests/
    ├── test_scheduler.py
    ├── test_resources.py
    ├── test_simulation.py
    └── test_metrics.py
```

---

# 4. Database

SQLite is the application's source of truth.

No real hospital database is required.

The application creates:

```text
medflow.db
```

Tables:

```text
patients
resources
allocations
departments
blood_inventory
medicine_inventory
equipment_inventory
simulation_runs
events
```

---

# 5. Patient Table

```text
Patient
-------
id
arrival_time
department
urgency
treatment_duration
waiting_time
priority_score
status
required_bed_type
doctor_required
nurses_required
or_required
ambulance_required
```

Medicine/equipment/blood requirements can initially be stored in a simple JSON field if implementation speed becomes a problem.

---

# 6. Resource Manager

Create a central resource manager.

Example interface:

```python
allocate_resource(patient, resource_type)
release_resource(resource_type)
is_available(resource_type)
get_available(resource_type)
```

Never allow individual scheduling modules to directly modify resource counts.

All resource changes should pass through `ResourceManager`.

This prevents inconsistent resource states.

---

# 7. Priority Engine

File:

```text
scheduling/priority.py
```

Implement:

```python
calculate_priority(patient, hospital_state)
```

Calculate:

```text
urgency_score
waiting_score
department_score
resource_feasibility
```

Then:

```text
priority =
0.60 * urgency
+ 0.20 * waiting
+ 0.10 * department
+ 0.10 * feasibility
```

Normalize scores between 0 and 1.

Keep the weights configurable.

---

# 8. Priority Queue

Use:

```python
heapq
```

Python's heap is a min-heap.

Therefore use:

```python
-priority_score
```

when inserting patients.

Example conceptual structure:

```python
(-priority_score, arrival_time, patient_id)
```

This also gives deterministic ordering when two patients have equal priority.

---

# 9. Scheduler

The scheduler should:

```text
1. Get waiting patients
2. Calculate priority
3. Insert into priority queue
4. Pop highest-priority patient
5. Check resources
6. Check inventory
7. Allocate if possible
8. Otherwise keep patient waiting
9. Continue
```

Never allocate a resource without checking availability first.

---

# 10. Scheduling Strategies

Create:

```text
scheduling/strategies.py
```

Implement:

```python
fcfs()
urgency_only()
medflow_hybrid()
```

All three should receive the same input scenario.

This allows fair comparison.

---

# 11. Simulation Engine

The simulation should be event-driven.

Example:

```text
00:00 PATIENT_ARRIVAL
00:04 PATIENT_ARRIVAL
00:07 TREATMENT_START
00:14 PATIENT_ARRIVAL
00:25 TREATMENT_COMPLETE
00:25 RESOURCE_RELEASE
```

Events:

```python
PATIENT_ARRIVAL
TREATMENT_START
TREATMENT_COMPLETE
RESOURCE_FAILURE
STAFF_SHORTAGE
EMERGENCY_SURGE
```

---

# 12. Resource Allocation

For every patient:

```text
Check:
├── Bed
├── ICU
├── Doctor
├── Nurse
├── OR
├── Ambulance
├── Blood
├── Medicine
└── Equipment
```

If all required resources are available:

```text
ALLOCATE
```

Otherwise:

```text
WAIT
```

Do not partially allocate resources unless you have an explicit rollback mechanism.

This prevents situations such as:

```text
Doctor allocated
ICU unavailable
Doctor remains falsely occupied
```

---

# 13. Inventory

## Blood

Track blood groups and units.

## Medicines

Track:

```text
name
quantity
minimum_threshold
```

## Equipment

Track:

```text
name
type
total_quantity
available_quantity
```

Reusable equipment is returned after treatment.

Consumable equipment is decremented.

---

# 14. Emergency Surge

Create a scenario generator.

Example:

```python
generate_emergency_surge(
    patients=20,
    duration=60
)
```

This adds a burst of patients to the event queue.

---

# 15. Staff Shortage

Scenario example:

```text
Doctors:
10 → 6

Nurses:
20 → 12
```

The Resource Manager should treat the missing staff as unavailable.

---

# 16. Resource Failure

Example:

```text
ICU Bed #4 → FAILED
```

The resource is marked unavailable.

The scheduler automatically stops allocating it.

---

# 17. Bottleneck Detection

Calculate utilization:

```text
utilization =
occupied_capacity / total_capacity
```

Example:

```text
ICU      94%
Doctors  89%
Beds     76%
OR       62%
```

A simple bottleneck rule:

```text
utilization >= 90%
```

→ bottleneck warning.

This threshold is a simulation setting.

---

# 18. Metrics

Calculate:

```text
patients_served
patients_waiting
average_waiting_time
maximum_waiting_time
critical_patient_wait
throughput
resource_utilization
resource_conflicts
blocked_patients
medicine_shortages
blood_shortages
```

---

# 19. ML Implementation

## Dataset Generation

Do not search for a hospital dataset.

Generate training data from the simulator.

Run many simulated scenarios.

Store:

```text
urgency
department
queue_length
icu_available
beds_available
doctors_available
nurses_available
treatment_duration
arrival_hour
actual_wait_time
```

The final column is the target:

```text
actual_wait_time
```

---

## Model

Start with:

```python
RandomForestRegressor
```

Train:

```text
80% training
20% testing
```

Calculate:

```text
MAE
R²
```

Save:

```text
ml/model.pkl
```

---

# 20. ML API

Create:

```text
POST /api/ml/predict-wait
```

Input:

```json
{
  "urgency": 4,
  "queue_length": 12,
  "icu_available": 1,
  "beds_available": 5,
  "doctors_available": 3,
  "nurses_available": 8,
  "treatment_duration": 30,
  "arrival_hour": 14
}
```

Return:

```json
{
  "predicted_wait_minutes": 18.4
}
```

---

# 21. Hugging Face Implementation

Hugging Face is an actual implemented feature, not just a README mention.

Create:

```text
ai/explainer.py
```

The backend first calculates the operational state.

Example:

```python
hospital_state = {
    "patients_waiting": 12,
    "critical_patients": 3,
    "average_wait": 24,
    "icu_utilization": 94,
    "bed_utilization": 81,
    "doctor_utilization": 89,
    "medicine_shortages": 2,
    "blood_shortages": 1,
    "bottleneck": "ICU"
}
```

Convert this structured state into a controlled prompt.

The Hugging Face model generates an explanation.

### Important

Do not send patient personal information.

Send only aggregated operational metrics.

The generated output should be displayed under:

```text
AI OPERATIONS INSIGHT
```

Example:

```text
ICU capacity is currently the primary operational bottleneck.
Three critical patients are waiting while ICU utilization
is above the configured threshold.
```

---

# 22. HF Fallback

Because this is an 8-hour hackathon, the application must not crash if the Hugging Face API/model is unavailable.

Implement:

```python
try:
    generate_ai_explanation()
except:
    generate_rule_based_explanation()
```

Fallback:

```text
ICU utilization is above 90%.
The current bottleneck is ICU capacity.
```

This ensures the demo always works.

---

# 23. Optimization

OR-Tools should be used after the basic scheduler works.

Optimization objective:

```text
MINIMIZE

waiting_time
+
critical_patient_delay
+
resource_conflicts
+
unused_capacity
```

Subject to:

```text
ICU allocation <= ICU capacity

Bed allocation <= bed capacity

Doctor allocation <= doctor capacity

Nurse allocation <= nurse capacity

OR allocation <= OR capacity

Medicine allocation <= inventory

Blood allocation <= inventory

Equipment allocation <= availability
```

If OR-Tools starts consuming too much development time, do not allow it to block the working prototype.

---

# 24. Flask API

Minimum endpoints:

```text
GET  /api/patients

POST /api/patients

GET  /api/resources

GET  /api/queue

POST /api/simulation/start

POST /api/simulation/reset

GET  /api/simulation/status

GET  /api/metrics

GET  /api/blood-bank

GET  /api/medicines

GET  /api/equipment

GET  /api/alerts

GET  /api/strategies/compare

POST /api/ml/predict-wait

POST /api/ai/explain
```

---

# 25. Frontend

The frontend should initially have ONE dashboard.

Do not waste time building ten pages.

Dashboard sections:

```text
HEADER

KPI CARDS

RESOURCE STATUS

PATIENT QUEUE

INVENTORY

ALERTS

ANALYTICS

AI OPERATIONS INSIGHT
```

Use Chart.js for:

* Utilization
* Waiting time
* Queue length
* Strategy comparison

---

# 26. Git Workflow

The team should work using branches.

```text
main
│
├── feature/scheduler
├── feature/backend
├── feature/frontend
└── feature/simulation
```

Basic workflow:

```bash
git clone <repo>
cd MEDFLOW

git checkout -b feature/scheduler

git add .
git commit -m "Implement priority scheduler"

git push -u origin feature/scheduler
```

Then create a Pull Request.

Do not allow everyone to directly modify `main`.

---

# 27. Definition of Done

The project is DONE when:

* Flask starts
* Database initializes
* Patients can be generated
* Queue works
* Priority works
* Resources are allocated
* Resource conflicts are prevented
* Simulation runs
* Inventory updates
* Metrics calculate
* Dashboard displays data
* Emergency scenario works
* Strategy comparison works
* ML prediction works
* Hugging Face explanation works
* Deployment works
* README works
* Demo scenario works

---

# 28. Development Priority

Implement in exactly this order:

```text
1. GitHub
2. Flask
3. SQLite
4. Patient model
5. Resource model
6. Priority algorithm
7. Queue
8. Resource allocation
9. Simulation
10. Metrics
11. Dashboard
12. Inventory
13. Scenarios
14. Strategy comparison
15. ML
16. Hugging Face
17. Optimization
18. Deployment
19. Demo polishing
```

Do not start with ML.

Do not start with Hugging Face.

Do not start with fancy UI.

The scheduler + simulation must work first.
