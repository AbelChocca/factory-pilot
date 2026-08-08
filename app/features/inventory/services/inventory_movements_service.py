from app.features.inventory.repositories.inventory_movement_repository import (
    InventoryMovementRepository,
)
from app.features.inventory.repositories.inventory_repository import InventoryRepository
from app.features.materials.repository import MaterialRepository
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.shared.pagination import PaginationHelper
from app.features.inventory.schema import (
    InventoryMovementFilterSchema,
    InventoryMovementResponseSchema,
    CreateInventoryMovementSchema
)
from app.features.inventory.types import InventoryOwnerType, InventoryMovementType
from app.shared.schema import PaginatedResponseSchema


class InventoryMovementService:
    def __init__(
        self,
        repository: InventoryMovementRepository,
        inventory_repository: InventoryRepository,
        material_repository: MaterialRepository
    ):
        self.repository = repository
        self.inventory_repository = inventory_repository
        self.material_repository = material_repository

    async def get(
        self,
        filters: InventoryMovementFilterSchema,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedResponseSchema[InventoryMovementResponseSchema]:

        offset = PaginationHelper.page_to_offset(
            page,
            limit,
        )

        movements = await self.repository.get(
            filters=filters,
            offset=offset,
            limit=limit,
        )

        total_items = await self.repository.count(filters)

        return PaginatedResponseSchema[InventoryMovementResponseSchema](
            items=[
                InventoryMovementResponseSchema.model_validate(movement)
                for movement in movements
            ],
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
        data: CreateInventoryMovementSchema,
    ) -> None:
        inventory = await self.inventory_repository.get_by_owner(
            owner_type=data.owner_type,
            owner_id=data.owner_id,
        )

        if inventory is None:
            raise ValueError("Inventory not found")

        prev_quantity = inventory.quantity

        if data.movement_type == InventoryMovementType.IN:
            new_quantity = inventory.quantity + data.quantity

        elif data.movement_type == InventoryMovementType.OUT:
            new_quantity = inventory.quantity - data.quantity

        elif data.movement_type == InventoryMovementType.ADJUSTMENT:
            new_quantity = data.quantity

        else:
            raise ValueError("Invalid movement type")

        await self.inventory_repository.update_quantity(
            owner_type=data.owner_type,
            owner_id=data.owner_id,
            quantity=new_quantity,
        )

        if data.owner_type == InventoryOwnerType.MATERIAL:
            entity = await self.material_repository.get_by_id(data.owner_id)
        else:
            entity = None

        movement = InventoryMovementTable(
            inventory_id=inventory.id,
            movement_type=data.movement_type,
            previous_quantity=prev_quantity,
            new_quantity=new_quantity,
            owner_code=entity.sku,
            owner_name=entity.name,
            unit_type=entity.unit_type,
            owner_type=data.owner_type,
            owner_id=data.owner_id,
            reason=data.reason,
            quantity=data.quantity,
        )

        await self.repository.save(movement)