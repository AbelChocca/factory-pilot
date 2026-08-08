from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
import secrets
import string

from app.shared.pagination import PaginationHelper
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.features.products.models.product import ProductTable
from app.features.products.repositories.product_repository import ProductRepository
from app.features.inventory.repositories.inventory_movement_repository import InventoryMovementRepository
from app.features.inventory.repositories.inventory_repository import InventoryRepository
from app.shared.schema import PaginatedResponseSchema
from app.features.products.schemas.product import (
    ProductFilterSchema,
    ProductResponseSchema,
    CreateProductSchema
)
from app.features.inventory.types import AvailabilityStatus
from app.features.inventory.types import InventoryOwnerType, InventoryMovementType
from app.shared.enums import Status
from app.shared.types import UnitType

class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        inventory_movement_repository: InventoryMovementRepository,
        inventory_repository: InventoryRepository
    ):
        self.product_repository = product_repository
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
        product: ProductTable,
        current_stock: Decimal,
        minimum_stock: Decimal,
    ) -> ProductResponseSchema:

        return ProductResponseSchema(
            id=product.id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            stock=current_stock,
            minimum_stock=minimum_stock,
            status=product.status,
            availability_status=self.calculate_availability(
                minimum_stock,
                current_stock,
            ),
        )

    async def get_by_id(
        self,
        material_id: UUID,
    ) -> ProductResponseSchema | None:

        product = await self.product_repository.get_by_id(material_id)

        inventory = await self.inventory_repository.get_by_owner(
            owner_type=InventoryOwnerType.PRODUCT,
            owner_id=product.id
        )

        if not product:
            return None

        return self.to_response(
            product,
            current_stock=inventory.quantity,
            minimum_stock=inventory.minimum_quantity
        )

    async def get(
        self,
        filters: ProductFilterSchema,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponseSchema[ProductResponseSchema]:

        offset = PaginationHelper.page_to_offset(
            page,
            limit,
        )

        total_items = await self.product_repository.count(filters)

        products = await self.product_repository.get(filters, offset, limit)

        products = [
            self.to_response(
                product,
                current_stock,
                minimum_stock
            )
            for product, current_stock, minimum_stock in products
        ]

        return PaginatedResponseSchema[ProductResponseSchema](
            items=products,
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
        schema: CreateProductSchema,
    ) -> CreateProductSchema:

        product = ProductTable(
            name=schema.name,
            sku=self.generate_sku(schema.name),
            description=schema.description,
            status=Status.ACTIVE,
        )

        product = await self.product_repository.save(product)

        inventory = await self.inventory_repository.save(
            InventoryTable(
                owner_type=InventoryOwnerType.PRODUCT,
                owner_id=product.id,
                quantity=schema.initial_stock,
                minimum_quantity=schema.initial_minimum_stock,
                last_movement_at=datetime.now(timezone.utc),
            )
        )

        await self.inventory_movement_repository.save(
            InventoryMovementTable(
                inventory_id=inventory.id,
                movement_type=InventoryMovementType.IN,
                previous_quantity=Decimal("0"),
                quantity=schema.initial_stock,
                new_quantity=schema.initial_stock,
                owner_name=product.name,
                owner_code=product.sku,
                unit_type=UnitType.UNIT,
                reason="Initial stock entry",
            )
        )

        return self.to_response(
            product,
            current_stock=inventory.quantity,
            minimum_stock=inventory.minimum_quantity,
        )

    async def delete(
        self,
        material_id: UUID,
    ) -> bool:

        return await self.product_repository.delete_by_id(material_id)

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