from .hospital import HospitalResources
from .blood_bank import BloodBank
from .medicine_inventory import MedicineInventory
from .equipment_inventory import EquipmentInventory

class ResourceManager:
    def __init__(self):
        self.hospital = HospitalResources()
        self.blood_bank = BloodBank()
        self.medicine = MedicineInventory()
        self.equipment = EquipmentInventory()

    # --- Unified Interfaces ---

    def is_available(self, resource_category, item_type, quantity=1):
        """
        Check if a resource is available.
        resource_category: 'hospital', 'blood', 'medicine', 'equipment_reusable', 'equipment_consumable'
        """
        if resource_category == 'hospital':
            return self.hospital.is_available(item_type, quantity)
        elif resource_category == 'blood':
            return self.blood_bank.check_blood(item_type, quantity)
        elif resource_category == 'medicine':
            return self.medicine.check_medicine(item_type, quantity)
        elif resource_category == 'equipment_reusable':
            return self.equipment.check_reusable_equipment(item_type, quantity)
        elif resource_category == 'equipment_consumable':
            return self.equipment.check_consumable_equipment(item_type, quantity)
        else:
            raise ValueError(f"Unknown resource category: {resource_category}")

    def allocate(self, resource_category, item_type, quantity=1):
        """
        Allocate or consume a resource.
        """
        if not self.is_available(resource_category, item_type, quantity):
            return False
            
        if resource_category == 'hospital':
            return self.hospital.allocate(item_type, quantity)
        elif resource_category == 'blood':
            return self.blood_bank.consume_blood(item_type, quantity)
        elif resource_category == 'medicine':
            return self.medicine.consume_medicine(item_type, quantity)
        elif resource_category == 'equipment_reusable':
            return self.equipment.allocate_equipment(item_type, quantity)
        elif resource_category == 'equipment_consumable':
            return self.equipment.consume_equipment(item_type, quantity)

    def release(self, resource_category, item_type, quantity=1):
        """
        Release a previously allocated reusable resource.
        Note: Blood, medicine, and consumable equipment cannot be released, only restocked.
        """
        if resource_category == 'hospital':
            return self.hospital.release(item_type, quantity)
        elif resource_category == 'equipment_reusable':
            return self.equipment.release_equipment(item_type, quantity)
        else:
            raise ValueError(f"Cannot release consumable category: {resource_category}. Use restock instead.")

    def get_status(self):
        """Get the full status of all resources and inventory."""
        return {
            "hospital": self.hospital.get_status(),
            "blood_bank": self.blood_bank.get_status(),
            "medicine": self.medicine.get_status(),
            "equipment": self.equipment.get_status()
        }
