class HospitalResources:
    def __init__(self, beds=50, icu=10, doctors=20, nurses=40, or_rooms=5, ambulances=5):
        self.capacities = {
            "bed": beds,
            "icu": icu,
            "doctor": doctors,
            "nurse": nurses,
            "or": or_rooms,
            "ambulance": ambulances
        }
        self.allocated = {
            "bed": 0,
            "icu": 0,
            "doctor": 0,
            "nurse": 0,
            "or": 0,
            "ambulance": 0
        }
        
    def is_available(self, resource_type, quantity=1):
        """Check if a specific quantity of a resource is available."""
        if resource_type not in self.capacities:
            raise ValueError(f"Unknown resource type: {resource_type}")
        
        available = self.capacities[resource_type] - self.allocated[resource_type]
        return available >= quantity

    def allocate(self, resource_type, quantity=1):
        """Allocate a specific quantity of a resource."""
        if not self.is_available(resource_type, quantity):
            return False
            
        self.allocated[resource_type] += quantity
        return True

    def release(self, resource_type, quantity=1):
        """Release a specific quantity of an allocated resource."""
        if resource_type not in self.allocated:
            raise ValueError(f"Unknown resource type: {resource_type}")
            
        if self.allocated[resource_type] < quantity:
            # Clamp to 0 to prevent negative allocations
            self.allocated[resource_type] = 0
            return True
            
        self.allocated[resource_type] -= quantity
        return True

    def get_status(self):
        """Get the current utilization status of all hospital resources."""
        status = {}
        for r_type in self.capacities.keys():
            cap = self.capacities[r_type]
            alloc = self.allocated[r_type]
            utilization = (alloc / cap * 100) if cap > 0 else 0
            status[r_type] = {
                "capacity": cap,
                "allocated": alloc,
                "available": cap - alloc,
                "utilization_percent": round(utilization, 2)
            }
        return status

    def simulate_failure(self, resource_type, quantity=1):
        """Temporarily reduce capacity (e.g., bed breaks, staff calls in sick)."""
        if resource_type in self.capacities:
            self.capacities[resource_type] = max(0, self.capacities[resource_type] - quantity)

    def resolve_failure(self, resource_type, quantity=1):
        """Restore capacity after a failure is resolved."""
        if resource_type in self.capacities:
            self.capacities[resource_type] += quantity
