class EquipmentInventory:
    def __init__(self, reusable_equipment=None, consumable_equipment=None):
        # Reusable equipment is allocated and released (e.g., ventilators, monitors)
        if reusable_equipment is None:
            self.reusable_capacities = {
                "ventilator": 15,
                "heart_monitor": 30,
                "defibrillator": 10
            }
        else:
            self.reusable_capacities = reusable_equipment.copy()
            
        self.reusable_allocated = {key: 0 for key in self.reusable_capacities}

        # Consumable equipment is simply decremented (e.g., syringes, bandages)
        if consumable_equipment is None:
            self.consumable_inventory = {
                "syringe": 5000,
                "bandage": 10000,
                "ppe": 2000
            }
        else:
            self.consumable_inventory = consumable_equipment.copy()

    # --- Reusable Equipment Methods ---

    def check_reusable_equipment(self, equipment_name, quantity=1):
        if equipment_name not in self.reusable_capacities:
            return False
        available = self.reusable_capacities[equipment_name] - self.reusable_allocated[equipment_name]
        return available >= quantity

    def allocate_equipment(self, equipment_name, quantity=1):
        if not self.check_reusable_equipment(equipment_name, quantity):
            return False
        self.reusable_allocated[equipment_name] += quantity
        return True

    def release_equipment(self, equipment_name, quantity=1):
        if equipment_name not in self.reusable_allocated:
            raise ValueError(f"Unknown equipment: {equipment_name}")
        
        if self.reusable_allocated[equipment_name] < quantity:
            self.reusable_allocated[equipment_name] = 0
        else:
            self.reusable_allocated[equipment_name] -= quantity
        return True

    # --- Consumable Equipment Methods ---

    def check_consumable_equipment(self, equipment_name, quantity=1):
        if equipment_name not in self.consumable_inventory:
            return False
        return self.consumable_inventory[equipment_name] >= quantity

    def consume_equipment(self, equipment_name, quantity=1):
        if not self.check_consumable_equipment(equipment_name, quantity):
            return False
        self.consumable_inventory[equipment_name] -= quantity
        return True

    def get_status(self):
        """Return the status of both reusable and consumable equipment."""
        reusable_status = {}
        for eq_type, cap in self.reusable_capacities.items():
            alloc = self.reusable_allocated[eq_type]
            reusable_status[eq_type] = {
                "capacity": cap,
                "allocated": alloc,
                "available": cap - alloc
            }
            
        return {
            "reusable": reusable_status,
            "consumable": self.consumable_inventory.copy()
        }
