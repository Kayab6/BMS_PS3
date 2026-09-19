class BloodBank:
    def __init__(self, initial_units=100):
        # We can expand to specific blood types later, for now we track total units
        # as a simplification if needed, or implement A+, O-, etc.
        self.inventory = {
            "A+": initial_units,
            "A-": initial_units,
            "B+": initial_units,
            "B-": initial_units,
            "AB+": initial_units,
            "AB-": initial_units,
            "O+": initial_units,
            "O-": initial_units
        }

    def check_blood(self, blood_type, quantity=1):
        """Check if sufficient units of a blood type are available."""
        if blood_type not in self.inventory:
            return False
        return self.inventory[blood_type] >= quantity

    def consume_blood(self, blood_type, quantity=1):
        """Consume units of a specific blood type."""
        if not self.check_blood(blood_type, quantity):
            return False
            
        self.inventory[blood_type] -= quantity
        return True

    def restock(self, blood_type, quantity):
        """Add units to the blood bank inventory."""
        if blood_type in self.inventory:
            self.inventory[blood_type] += quantity
            
    def get_status(self):
        """Return the current inventory status of all blood types."""
        return self.inventory.copy()
