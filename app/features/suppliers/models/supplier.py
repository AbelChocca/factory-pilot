from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.shared.enums import Status


class SupplierTable(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    name: str = Field(
        max_length=150,
        nullable=False,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    lead_time_days: int = Field(
        nullable=False,
    )

    status: Status = Field(
        nullable=False,
    )