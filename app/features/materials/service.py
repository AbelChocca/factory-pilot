from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
import secrets
import string

from app.features.materials.model import MaterialTable
from app.shared.pagination import PaginationHelper
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.features.materials.repository import MaterialRepository
from app.features.inventory.repositories.inventory_movement_repository import InventoryMovementRepository
from app.features.inventory.repositories.inventory_repository import InventoryRepository
from app.shared.schema import PaginatedResponseSchema
from app.features.materials.schema import (
    MaterialFilterSchema,
    MaterialResponseSchema,
    CreateMaterialSchema
)
from app.features.inventory.types import AvailabilityStatus
from app.features.inventory.types import InventoryOwnerType, InventoryMovementType
from app.shared.enums import Status

class MaterialService:
    def __init__(
        self,
        material_repository: MaterialRepository,
        inventory_movement_repository: InventoryMovementRepository,
        inventory_repository: InventoryRepository
    ):
        self.material_repository = material_repository
        self.inventory_movement_repository = inventory_movement_repository
        self.inventory_repository = inventory_repository

    def calculate_availability(
        self,
        minimum_stock: Decimal,
        current_stock: Decimal,
    ) -> AvailabilityStatus:

        if current_stock <= Decimal("0"):
            return AvailabilityStatus.OUT_OF_STOCK

        if current_stock < minimum_stock:
            return AvailabilityStatus.LOW_STOCK

        return AvailabilityStatus.AVAILABLE

    def to_response(
        self,
        material: MaterialTable,
        current_stock: Decimal,
        minimum_stock: Decimal
    ) -> MaterialResponseSchema:

        return MaterialResponseSchema(
            id=material.id,
            sku=material.sku,
            name=material.name,
            description=material.description,
            stock=current_stock,
            minimum_stock=minimum_stock,
            unit=material.unit_type,
            status=material.status,
            availability_status=self.calculate_availability(minimum_stock, current_stock),
        )

    async def get_by_id(
        self,
        material_id: UUID,
    ) -> MaterialResponseSchema | None:

        material = await self.material_repository.get_by_id(material_id)

        inventory = await self.inventory_repository.get_by_owner(
            owner_type=InventoryOwnerType.MATERIAL,
            owner_id=material.id
        )

        if not material:
            return None

        return self.to_response(
            material,
            current_stock=inventory.quantity,
            minimum_stock=inventory.minimum_quantity
        )

    async def get(
        self,
        filters: MaterialFilterSchema,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponseSchema[MaterialResponseSchema]:

        offset = PaginationHelper.page_to_offset(
            page,
            limit,
        )

        total_items = await self.material_repository.count(filters)

        materials = await self.material_repository.get(filters, offset, limit)

        materials = [
            self.to_response(
                material,
                current_stock,
                minimum_stock
            )
            for material, current_stock, minimum_stock in materials
        ]

        return PaginatedResponseSchema[MaterialResponseSchema](
            items=materials,
            total_items=total_items,
            total_pages=PaginationHelper.total_pages(
                total_items,
                limit,
            ),
            current_page=PaginationHelper.offset_to_page(
                offset,
                limit,
            ),
        )

    async def create(
        self,
        schema: CreateMaterialSchema,
    ) -> MaterialResponseSchema:

        material = MaterialTable(
            name=schema.name,
            sku=self.generate_sku(schema.name),
            description=schema.description,
            material_type=schema.material_type,
            unit_type=schema.unit_type,
            status=Status.ACTIVE
        )

        material = await self.material_repository.save(material)

        inventory = await self.inventory_repository.save(
            inventory=InventoryTable(
                owner_type=InventoryOwnerType.MATERIAL,
                owner_id=material.id,
                quantity=schema.initial_stock,
                minimum_quantity=schema.initial_minimum_stock,
                last_movement_at=datetime.now(timezone.utc)
            )
        )

        await self.inventory_movement_repository.save(
            InventoryMovementTable(
                inventory_id=inventory.id,
                movement_type=InventoryMovementType.IN,
                previous_quantity=Decimal("0"),
                quantity=schema.initial_stock,
                new_quantity=schema.initial_stock,
                owner_name=material.name,
                owner_code=material.sku,
                unit_type=material.unit_type,
                reason="Initial stock entry"
            )
        )

        return MaterialResponseSchema(
            id=material.id,
            sku=material.sku,
            name=material.name,
            description=material.description,
            unit=material.unit_type,
            stock=inventory.quantity,
            minimum_stock=inventory.minimum_quantity,
            status=material.status,
            availability_status=self.calculate_availability(inventory.minimum_quantity, inventory.quantity)
        )

    async def delete(
        self,
        material_id: UUID,
    ) -> bool:

        return await self.material_repository.delete_by_id(material_id)

    def generate_sku(
        self,
        name: str,
    ) -> str:

        words = [
            word
            for word in name.upper().split()
            if word.isalnum()
        ]

        abbreviation = "".join(
            word[0]
            for word in words
        )[:3]

        if len(abbreviation) < 3:
            abbreviation = abbreviation.ljust(3, "X")

        characters = string.ascii_uppercase + string.digits

        random_code = "".join(
            secrets.choice(characters)
            for _ in range(6)
        )

        return f"{abbreviation}-{random_code}"