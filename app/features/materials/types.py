from enum import Enum


class MaterialType(str, Enum):
    RAW_MATERIAL = "RAW_MATERIAL"
    ACCESSORY = "ACCESSORY"
    PACKAGING = "PACKAGING"
    CONSUMABLE = "CONSUMABLE"