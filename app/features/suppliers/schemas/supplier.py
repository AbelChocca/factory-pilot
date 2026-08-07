from app.shared.enums import Status
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID

class SupplierFilterSchema(BaseModel):
    query: str | None = None
    status: Status | None = None

class CreateSupplierSchema(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    lead_time_days: int = Field(ge=0)


class SupplierResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr | None
    phone: str | None
    lead_time_days: int
    status: Status