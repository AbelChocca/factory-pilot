from enum import Enum

class OperationalStatus(str, Enum):
    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"

class ProcurementPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaterialCoverageStatus(str, Enum):
    CRITICAL = "critical"
    LOW = "low"
    HEALTHY = "healthy"
    NO_CONSUMPTION = "no_consumption"