class MedicineInventory:
    def __init__(self, initial_quantities=None):
        if initial_quantities is None:
            # Default mock quantities
            self.inventory = {
                "painkillers": 1000,
                "antibiotics": 500,
                "anesthetics": 200,
                "iv_fluids": 2000
            }
        else:
            self.inventory = initial_quantities.copy()

    def check_medicine(self, medicine_name, quantity=1):
        """Check if sufficient quantity of a medicine is available."""
        if medicine_name not in self.inventory:
            return False
        return self.inventory[medicine_name] >= quantity

    def consume_medicine(self, medicine_name, quantity=1):
        """Consume a specific quantity of a medicine."""
        if not self.check_medicine(medicine_name, quantity):
            return False
            
        self.inventory[medicine_name] -= quantity
        return True
        
    def restock(self, medicine_name, quantity):
        """Add stock to a specific medicine."""
        if medicine_name not in self.inventory:
            self.inventory[medicine_name] = 0
        self.inventory[medicine_name] += quantity

    def get_status(self):
        """Return the current inventory levels of all medicines."""
        return self.inventory.copy()
