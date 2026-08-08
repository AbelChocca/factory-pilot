from enum import StrEnum


class PurchasePlanStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    CANCELLED = "cancelled"