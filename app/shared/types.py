from enum import Enum

class UnitType(str, Enum):
    UNIT = "UNIT" 

    KILOGRAM = "KG" 
    GRAM = "G"

    METER = "M"   
    SQUARE_METER = "M2"

    LITER = "L" 

    BOX = "BOX" 
    ROLL = "ROLL" 