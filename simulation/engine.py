import heapq
from .events import SimulationEvent, EventType
from .generator import generate_scenario
from resources.manager import ResourceManager

class SimulationEngine:
    def __init__(self):
        self.event_queue = []
        self.resource_manager = ResourceManager()
        self.current_time = 0
        self.waiting_queue = []
        
        # Metrics
        self.metrics = {
            "patients_served": 0,
            "patients_waiting": 0,
            "total_wait_time": 0,
            "bottlenecks_hit": 0
        }

    def load_scenario(self, scenario_type="normal", duration_mins=1440):
        raw_events = generate_scenario(scenario_type, duration_mins)
        for e in raw_events:
            event_type = EventType[e["event_type"]]
            patient = e.get("patient", None)
            payload = e.get("payload", None)
            
            event = SimulationEvent(
                time=e["time"], 
                event_type=event_type, 
                patient_id=patient["id"] if patient else None,
                payload=patient if patient else payload
            )
            heapq.heappush(self.event_queue, event)

    def process_waiting_queue(self):
        """
        Dummy scheduling logic. To be replaced by the actual Scheduler.
        For now, simply checks if basic resources are available for the first person in line.
        """
        if not self.waiting_queue:
            return
            
        patient = self.waiting_queue[0]
        
        # Check resources (Simplified for MVP)
        can_allocate = True
        
        if patient["needs_icu"] and not self.resource_manager.is_available('hospital', 'icu'):
            can_allocate = False
        elif not patient["needs_icu"] and not self.resource_manager.is_available('hospital', 'bed'):
            can_allocate = False
            
        if patient["needs_doctor"] and not self.resource_manager.is_available('hospital', 'doctor'):
            can_allocate = False
            
        if patient["needs_medicine"] and not self.resource_manager.is_available('medicine', 'painkillers'):
            can_allocate = False
            
        if can_allocate:
            self.waiting_queue.pop(0)
            
            # Allocate
            if patient["needs_icu"]:
                self.resource_manager.allocate('hospital', 'icu')
            else:
                self.resource_manager.allocate('hospital', 'bed')
                
            if patient["needs_doctor"]:
                self.resource_manager.allocate('hospital', 'doctor')
            if patient["needs_medicine"]:
                self.resource_manager.allocate('medicine', 'painkillers')
                
            patient["status"] = "IN_TREATMENT"
            wait_time = self.current_time - patient["arrival_time"]
            self.metrics["total_wait_time"] += wait_time
            
            # Schedule TREATMENT_COMPLETE
            completion_time = self.current_time + patient["treatment_duration"]
            heapq.heappush(self.event_queue, SimulationEvent(
                time=completion_time,
                event_type=EventType.TREATMENT_COMPLETE,
                patient_id=patient["id"],
                payload=patient
            ))
        else:
            self.metrics["bottlenecks_hit"] += 1

    def run_simulation(self, scenario_type="normal"):
        self.load_scenario(scenario_type)
        
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if event.event_type == EventType.PATIENT_ARRIVAL:
                patient = event.payload
                self.waiting_queue.append(patient)
                
            elif event.event_type == EventType.TREATMENT_COMPLETE:
                patient = event.payload
                patient["status"] = "DISCHARGED"
                self.metrics["patients_served"] += 1
                
                # Release resources
                if patient["needs_icu"]:
                    self.resource_manager.release('hospital', 'icu')
                else:
                    self.resource_manager.release('hospital', 'bed')
                if patient["needs_doctor"]:
                    self.resource_manager.release('hospital', 'doctor')
                
            elif event.event_type == EventType.STAFF_SHORTAGE:
                res = event.payload["resource"]
                qty = event.payload["quantity_missing"]
                self.resource_manager.hospital.simulate_failure(res, qty)
                
            elif event.event_type == EventType.RESOURCE_FAILURE:
                res = event.payload["resource"]
                qty = event.payload["quantity"]
                dur = event.payload["duration"]
                self.resource_manager.hospital.simulate_failure(res, qty)
                
                # Schedule restoration
                heapq.heappush(self.event_queue, SimulationEvent(
                    time=self.current_time + dur,
                    event_type=EventType.RESOURCE_RESTORED,
                    payload={"resource": res, "quantity": qty}
                ))
                
            elif event.event_type == EventType.RESOURCE_RESTORED:
                res = event.payload["resource"]
                qty = event.payload["quantity"]
                self.resource_manager.hospital.resolve_failure(res, qty)
                
            # Try to process waiting queue at each time step
            self.process_waiting_queue()
            
        self.metrics["patients_waiting"] = len(self.waiting_queue)
        
        return {
            "status": "COMPLETED",
            "scenario": scenario_type,
            "simulated_time": self.current_time,
            "metrics": self.metrics,
            "final_resources": self.resource_manager.get_status()
        }

def run_simulation(scenario_type="normal"):
    """Entry point for testing."""
    engine = SimulationEngine()
    return engine.run_simulation(scenario_type)
