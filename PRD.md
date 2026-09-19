# MEDFLOW

## Prioritize Patients. Optimize Resources.

**Version:** 1.0
**Project Type:** Hospital Resource Management Simulator
**Hackathon:** 24-Hour Hackathon
**Prototype Target:** Deployable within first 8 hours

---

# 1. Product Overview

MEDFLOW is a hospital operations simulation platform that simulates patient arrivals and intelligently allocates constrained hospital resources.

The system considers:

* Patient urgency
* Waiting time
* Department priority
* Bed availability
* ICU availability
* Doctors
* Nurses
* Operating rooms
* Ambulances
* Blood inventory
* Medicine inventory
* Medical equipment
* Resource conflicts
* Capacity constraints
* Operational bottlenecks

MEDFLOW provides a real-time operations dashboard showing the current hospital state, patient queue, resource utilization, shortages, alerts and scheduling performance.

The system also compares different scheduling strategies and uses machine learning to provide operational predictions.

A Hugging Face model is used as an **operations explanation layer**, converting structured simulation results into human-readable explanations.

The AI model does not make clinical decisions or override scheduling constraints.

---

# 2. Problem Statement

Hospitals operate with finite resources while patients arrive continuously with different urgency levels and resource requirements.

Poor resource allocation can lead to:

* Long patient waiting times
* ICU overload
* Staff conflicts
* Operating-room conflicts
* Equipment shortages
* Medicine shortages
* Blood shortages
* Underutilized resources
* Delayed emergency treatment

MEDFLOW simulates this environment and provides an operational scheduling system that attempts to prioritize patients while respecting resource constraints.

---

# 3. Objectives

The system must:

1. Simulate patient arrivals.
2. Assign patients urgency levels.
3. Maintain a dynamic patient queue.
4. Calculate patient priority.
5. Consider department-level operational priority.
6. Track waiting time.
7. Track hospital resources.
8. Allocate resources without conflicts.
9. Respect capacity limits.
10. Track resource utilization.
11. Track medicines and equipment.
12. Track blood inventory.
13. Detect shortages.
14. Simulate emergency surges.
15. Simulate staff shortages.
16. Compare scheduling strategies.
17. Detect operational bottlenecks.
18. Predict operational outcomes using ML.
19. Explain simulation results using Hugging Face.
20. Display all important information through a dashboard.

---

# 4. Target Users

## Primary User

Hospital operations manager / administrator.

## Secondary Users

* Resource planners
* Hospital staff
* Researchers
* Students
* Hackathon judges

MEDFLOW is a simulation and educational prototype and is not intended for real clinical decision-making.

---

# 5. Core Patient Model

Every simulated patient contains:

* Patient ID
* Arrival time
* Department
* Urgency level
* Treatment duration
* Required bed type
* Required doctor
* Required nurses
* Required operating room
* Required ambulance where applicable
* Required medicines
* Required blood type/units
* Required equipment
* Current waiting time
* Priority score
* Status

Possible patient statuses:

```text
WAITING
ALLOCATED
IN_TREATMENT
COMPLETED
BLOCKED
```

---

# 6. Department Priority

MEDFLOW includes a configurable department priority factor.

Example simulation configuration:

```text
Emergency        5
Trauma           5
ICU              5
Cardiology       4
Neurology        4
Gynecology       4
General Surgery  4
Pediatrics       4
Orthopedics      3
Dermatology      2
Routine OPD      1
```

These values are simulation-policy assumptions, not medical facts.

Department priority must never completely override patient urgency.

For example, a highly urgent patient in a lower-priority department may still outrank a routine patient from a higher-priority department.

---

# 7. Patient Priority Algorithm

MEDFLOW uses a weighted priority score.

```text
Priority Score =
    0.60 × Urgency Score
  + 0.20 × Waiting-Time Score
  + 0.10 × Department Priority
  + 0.10 × Resource Feasibility
```

All components are normalized.

The weights should be configurable.

The scheduler uses a priority queue to determine which waiting patient should be considered next.

---

# 8. Scheduling Strategies

MEDFLOW supports three strategies.

## Strategy 1 — FCFS

First Come First Serve.

Patients are processed according to arrival time.

## Strategy 2 — Urgency Only

Patients with higher urgency are processed first.

## Strategy 3 — MEDFLOW Hybrid

Considers:

* Urgency
* Waiting time
* Department priority
* Resource feasibility

All strategies must operate on the same simulated scenario so their performance can be compared fairly.

---

# 9. Hospital Resources

## Capacity Resources

* General beds
* ICU beds
* Doctors
* Nurses
* Operating rooms
* Ambulances

## Inventory Resources

* Blood
* Medicines
* Consumable equipment

## Reusable Equipment

Examples:

* Surgical scissors
* Clamps
* Forceps
* Patient monitors
* BP monitors
* Ventilators
* Wheelchairs

## Consumable Equipment

Examples:

* Syringes
* Gloves
* IV sets
* Bandages
* Catheters

Reusable resources:

```text
AVAILABLE → IN USE → AVAILABLE
```

Consumables:

```text
INVENTORY → CONSUMED
```

---

# 10. Blood Bank

MEDFLOW tracks:

* A+
* A-
* B+
* B-
* AB+
* AB-
* O+
* O-

The simulator checks whether required blood inventory is available before treatment.

If insufficient inventory exists:

```text
Patient → BLOCKED/WAITING
Blood inventory → shortage alert
```

---

# 11. Medicine Inventory

Each medicine contains:

* Medicine ID
* Medicine name
* Quantity
* Minimum threshold
* Unit
* Status

Possible statuses:

```text
NORMAL
LOW
CRITICAL
OUT_OF_STOCK
```

The system generates alerts when inventory falls below thresholds.

---

# 12. Equipment Inventory

Equipment records contain:

* Equipment ID
* Equipment name
* Equipment type
* Total quantity
* Available quantity
* Status

The scheduler checks equipment availability before allocating a treatment.

---

# 13. Simulation Engine

MEDFLOW uses discrete-event simulation.

Events include:

```text
PATIENT_ARRIVAL
TREATMENT_START
TREATMENT_COMPLETE
RESOURCE_FAILURE
STAFF_SHORTAGE
EMERGENCY_SURGE
MEDICINE_SHORTAGE
BLOOD_SHORTAGE
```

The simulator jumps between important events instead of processing every real-world second.

---

# 14. Emergency Surge

The system can generate a sudden increase in patient arrivals.

Example:

```text
Normal:
5 patients/hour

Emergency surge:
20 patients/hour
```

The dashboard should show:

* Queue growth
* Resource utilization
* Waiting time
* Bottleneck
* Emergency patient count

---

# 15. Staff Shortage

The simulator can reduce:

* Doctors
* Nurses

Example:

```text
Normal doctors = 10
Shortage scenario = 6
```

The system should show the resulting effect on:

* Waiting time
* Queue length
* Throughput
* Resource utilization

---

# 16. Resource Failure

A resource can become unavailable.

Examples:

```text
ICU bed unavailable
Operating room unavailable
Doctor unavailable
Ventilator unavailable
```

The scheduler must not allocate unavailable resources.

---

# 17. Operational Prediction

Machine learning is used for operational prediction.

Primary ML task:

### Patient waiting-time prediction

Features:

* Urgency
* Department
* Queue length
* ICU availability
* Bed availability
* Doctor availability
* Nurse availability
* Treatment duration
* Arrival hour
* Required resources

Output:

```text
Predicted waiting time
```

Secondary prediction, if time permits:

### Resource demand prediction

Predict expected demand for:

* ICU
* Beds
* Doctors
* Nurses
* Medicines

ML predictions are advisory and cannot violate hard resource constraints.

---

# 18. Hugging Face AI Explanation Layer

Hugging Face must be implemented in the final prototype.

The model receives structured operational information.

Example:

```json
{
  "patients_waiting": 12,
  "critical_patients": 3,
  "average_wait": 24,
  "icu_utilization": 94,
  "bed_utilization": 81,
  "doctor_utilization": 89,
  "blood_shortages": 1,
  "medicine_shortages": 2,
  "main_bottleneck": "ICU"
}
```

The model generates an operational explanation such as:

```text
ICU capacity is currently the primary bottleneck.
Three critical patients are waiting while ICU utilization
has reached 94%. Medicine shortages are also contributing
to treatment delays.
```

The model must NOT:

* Decide who receives treatment
* Override resource constraints
* Diagnose patients
* Recommend clinical treatment
* Make medical decisions

It is an explanation and reporting layer.

---

# 19. Dashboard

The dashboard must display:

## KPI Cards

* Patients served
* Patients waiting
* Critical patients
* Average waiting time
* Maximum waiting time
* ICU utilization
* Overall resource utilization

## Resource Panel

```text
General Beds      14 / 20
ICU Beds           5 / 6
Doctors            8 / 10
Nurses            15 / 20
Operating Rooms    3 / 4
Ambulances         4 / 6
```

## Patient Queue

Columns:

* Patient ID
* Department
* Urgency
* Waiting time
* Priority
* Required resources
* Status

## Inventory

* Blood
* Medicines
* Equipment

## Alerts

Examples:

```text
CRITICAL: ICU utilization 94%

WARNING: O- blood below threshold

WARNING: Emergency medicine stock low

BOTTLENECK: ICU
```

## Analytics

Charts:

* Waiting-time distribution
* Resource utilization
* Queue length
* Patients served
* Strategy comparison

---

# 20. Strategy Comparison

The system compares:

```text
FCFS
vs
Urgency Only
vs
MEDFLOW
```

Metrics:

* Average waiting time
* Maximum waiting time
* Critical-patient waiting time
* Patients served
* Resource utilization
* Resource conflicts
* Blocked patients

The dashboard visualizes these results.

---

# 21. Success Criteria

The prototype is successful if it can demonstrate:

```text
Patient arrives
      ↓
Urgency assigned
      ↓
Priority calculated
      ↓
Queue created
      ↓
Resources checked
      ↓
Resources allocated
      ↓
Treatment simulated
      ↓
Resources released
      ↓
Inventory updated
      ↓
Metrics calculated
      ↓
Dashboard updated
      ↓
ML prediction
      ↓
Hugging Face explanation
```

---

# 22. Scope Exclusions

Do not implement:

* Real patient data
* Real clinical recommendations
* Real hospital deployment
* Real transplant allocation
* Detailed medical diagnosis
* Real-world clinical protocols
* Complex pharmaceutical pharmacology
* Real emergency dispatch integration

---

# 23. Hackathon Demo

The final demonstration should show:

1. Normal hospital operation.
2. Patient arrivals.
3. Priority queue.
4. Resource allocation.
5. Emergency surge.
6. ICU bottleneck.
7. Medicine/blood shortage.
8. Strategy comparison.
9. ML waiting-time prediction.
10. Hugging Face operational explanation.
11. Dashboard metrics.

The demo should finish with a clear comparison showing how the MEDFLOW strategy handles the simulated operational scenario.
