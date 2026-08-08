from enum import StrEnum

class InventoryOwnerType(StrEnum):
    PRODUCT = "PRODUCT"
    MATERIAL = "MATERIAL"

class InventoryMovementType(StrEnum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"

class AvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"