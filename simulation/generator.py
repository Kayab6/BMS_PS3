import random

def generate_patient(patient_id, arrival_time, is_emergency=False):
    """Generate a single synthetic patient."""
    urgency = random.randint(4, 5) if is_emergency else random.randint(1, 4)
    
    # 20% chance of needing ICU for high urgency
    needs_icu = True if urgency >= 4 and random.random() < 0.2 else False
    
    return {
        "id": patient_id,
        "arrival_time": arrival_time,
        "urgency": urgency,
        "needs_icu": needs_icu,
        "needs_doctor": True,
        "needs_medicine": random.random() < 0.8,
        "treatment_duration": random.randint(15, 120),  # minutes
        "status": "WAITING"
    }

def generate_scenario(scenario_type="normal", duration_mins=1440):
    """
    Generate an event queue scenario. 
    Duration is in minutes (e.g., 1440 = 24 hours).
    Returns a list of raw event dictionaries to be loaded into the engine.
    """
    events = []
    patient_count = 1
    
    if scenario_type == "normal":
        # Average 1 patient every 15 minutes
        time = 0
        while time < duration_mins:
            time += int(random.expovariate(1.0 / 15.0))
            if time < duration_mins:
                events.append({
                    "time": time,
                    "event_type": "PATIENT_ARRIVAL",
                    "patient": generate_patient(f"P{patient_count:03d}", time)
                })
                patient_count += 1
                
    elif scenario_type == "emergency_surge":
        # Normal traffic plus a massive surge at hour 4 (minute 240)
        time = 0
        while time < duration_mins:
            time += int(random.expovariate(1.0 / 15.0))
            if time < duration_mins:
                events.append({
                    "time": time,
                    "event_type": "PATIENT_ARRIVAL",
                    "patient": generate_patient(f"P{patient_count:03d}", time)
                })
                patient_count += 1
                
        # The Surge
        for i in range(20):
            events.append({
                "time": 240 + random.randint(0, 30),
                "event_type": "PATIENT_ARRIVAL",
                "patient": generate_patient(f"SURGE_{i:02d}", 240, is_emergency=True)
            })
            
    elif scenario_type == "staff_shortage":
        # Normal traffic but 4 doctors call in sick at hour 2
        events = generate_scenario("normal", duration_mins)
        events.append({
            "time": 120,
            "event_type": "STAFF_SHORTAGE",
            "payload": {"resource": "doctor", "quantity_missing": 4}
        })
        
    elif scenario_type == "resource_failure":
        events = generate_scenario("normal", duration_mins)
        events.append({
            "time": 300,
            "event_type": "RESOURCE_FAILURE",
            "payload": {"resource": "icu", "quantity": 1, "duration": 180}
        })
        
    elif scenario_type == "inventory_shortage":
        # Simulate an inventory shortage event
        events = generate_scenario("normal", duration_mins)
        events.append({
            "time": 180,
            "event_type": "RESOURCE_FAILURE",
            "payload": {"resource": "painkillers", "quantity": 500, "duration": 360}
        })
        
    # Sort events chronologically just in case
    events.sort(key=lambda x: x["time"])
    return events
