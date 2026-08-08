from enum import Enum

class ProductionRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConsumptionTrend(str, Enum):
    DECREASING = "DECREASING"
    STABLE = "STABLE"
    INCREASING = "INCREASING"

class ProductionRiskFactorType(str, Enum):
    LOW_STOCK = "LOW_STOCK"
    LOW_STOCK_COVERAGE = "LOW_STOCK_COVERAGE"
    PRODUCTION_BOTTLENECK = "PRODUCTION_BOTTLENECK"
    SUPPLIER_LEAD_TIME = "SUPPLIER_LEAD_TIME"
    INCREASING_CONSUMPTION = "INCREASING_CONSUMPTION"
    NO_SUPPLIER = "NO_SUPPLIER"

class MaterialImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"