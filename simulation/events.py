from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class EventType(Enum):
    PATIENT_ARRIVAL = "PATIENT_ARRIVAL"
    TREATMENT_START = "TREATMENT_START"
    TREATMENT_COMPLETE = "TREATMENT_COMPLETE"
    RESOURCE_FAILURE = "RESOURCE_FAILURE"
    RESOURCE_RESTORED = "RESOURCE_RESTORED"
    EMERGENCY_SURGE = "EMERGENCY_SURGE"
    STAFF_SHORTAGE = "STAFF_SHORTAGE"

@dataclass(order=True)
class SimulationEvent:
    time: int
    event_type: EventType = field(compare=False)
    patient_id: str = field(default=None, compare=False)
    payload: Any = field(default=None, compare=False)
