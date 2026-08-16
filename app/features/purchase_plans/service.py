from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.features.purchase_plans.model import (
    PurchasePlanItemTable,
    PurchasePlanTable,
)
from app.features.purchase_plans.schema import CreatePurchasePlanSchema, UpdatePurchasePlanSchema, PurchasePlanItem, PurchasePlanResponseSchema
from app.features.purchase_plans.repository import (
    PurchasePlanRepository,
)
from app.features.purchase_plans.types import PurchasePlanStatus
from app.features.suppliers.repositories.supplier_material_repository import (
    SupplierMaterialRepository
)
from app.shared.schema import PaginatedResponseSchema


class PurchasePlanService:

    def __init__(
        self,
        purchase_plan_repository: PurchasePlanRepository,
        supplier_material_repository: SupplierMaterialRepository,
    ):
        self.purchase_plan_repository = purchase_plan_repository
        self.supplier_material_repository = (
            supplier_material_repository
        )

    async def get_items(
        self,
        purchase_plan_id: UUID,
    ) -> list[PurchasePlanItem]:

        return await self.purchase_plan_repository.get_items(
            purchase_plan_id,
        )

    async def get_by_id(
        self,
        purchase_plan_id: UUID,
    ) -> PurchasePlanTable | None:

        return await self.purchase_plan_repository.get_by_id(
            purchase_plan_id,
        )

    async def get_all(
        self,
        page: int,
        limit: int,
        search: str | None = None
    ) -> PaginatedResponseSchema[PurchasePlanResponseSchema]:
        items, total_items = await (
            self.purchase_plan_repository.get_all(
                page=page,
                limit=limit,
                search=search,
            )
        )

        total_pages = (
            (total_items + limit - 1) // limit
            if total_items
            else 0
        )

        return PaginatedResponseSchema(
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=page
        )

    async def get_current(
        self,
    ) -> PurchasePlanTable | None:

        return await self.purchase_plan_repository.get_current()

    async def create(
        self,
        schema: CreatePurchasePlanSchema,
    ) -> PurchasePlanTable:

        material_ids = [
            item.material_id
            for item in schema.items
        ]

        relations = (
            await self.supplier_material_repository
            .get_preferred_by_material_ids(material_ids)
        )

        relation_map = {
            relation.material_id: relation
            for relation in relations
        }

        items: list[PurchasePlanItemTable] = []

        for item_schema in schema.items:

            relation = relation_map.get(
                item_schema.material_id
            )

            if relation is None:
                raise ValueError(
                    "Preferred supplier is not associated with material."
                )

            estimated_cost = (
                item_schema.quantity
                * relation.unit_price
            )

            items.append(
                PurchasePlanItemTable(
                    material_id=item_schema.material_id,
                    supplier_id=relation.supplier_id,
                    quantity=item_schema.quantity,
                    unit_price=relation.unit_price,
                    estimated_cost=estimated_cost,
                    lead_time_days=relation.lead_time_days,
                    preferred_supplier=relation.preferred,
                )
            )

        purchase_plan = PurchasePlanTable(
            status=PurchasePlanStatus.DRAFT,
            items=items,
        )

        purchase_plan.total_estimated_cost = sum(
            (
                item.estimated_cost
                for item in items
            ),
            Decimal("0"),
        )

        return await self.purchase_plan_repository.save(
            purchase_plan,
        )

    async def update(
        self,
        purchase_plan_id: UUID,
        schema: UpdatePurchasePlanSchema,
    ) -> PurchasePlanTable | None:

        purchase_plan = await self.get_by_id(
            purchase_plan_id,
        )

        if not purchase_plan:
            return None

        self._ensure_editable(
            purchase_plan,
        )

        material_ids = [
            item.material_id
            for item in schema.items
        ]

        relations = (
            await self.supplier_material_repository
            .get_by_material_ids(material_ids)
        )

        relation_map = {
            (
                relation.material_id,
                relation.supplier_id,
            ): relation
            for relation in relations
        }

        new_items = []

        for item_schema in schema.items:

            if item_schema.quantity <= Decimal("0"):
                raise ValueError(
                    "Purchase quantity must be greater than zero."
                )

            relation = relation_map.get(
                (
                    item_schema.material_id,
                    item_schema.supplier_id,
                )
            )

            if relation is None:
                raise ValueError(
                    "Supplier is not associated with material."
                )

            estimated_cost = (
                item_schema.quantity
                * relation.unit_price
            )

            new_items.append(
                PurchasePlanItemTable(
                    purchase_plan_id=purchase_plan.id,
                    material_id=item_schema.material_id,
                    supplier_id=item_schema.supplier_id,
                    quantity=item_schema.quantity,
                    unit_price=relation.unit_price,
                    estimated_cost=estimated_cost,
                    lead_time_days=relation.lead_time_days,
                    preferred_supplier=relation.preferred,
                )
            )

        # Replace entire draft state
        purchase_plan.items = new_items

        self._calculate_total_cost(
            purchase_plan,
        )

        purchase_plan.updated_at = datetime.now(
            timezone.utc,
        )

        return await self.purchase_plan_repository.replace_items(
            purchase_plan,
        )

    async def approve(
        self,
        purchase_plan_id: UUID,
    ) -> PurchasePlanTable | None:

        purchase_plan = await self.get_by_id(
            purchase_plan_id,
        )

        if not purchase_plan:
            return None

        self._ensure_editable(
            purchase_plan,
        )

        if not purchase_plan.items:
            raise ValueError(
                "Cannot approve an empty purchase plan.",
            )

        purchase_plan.status = PurchasePlanStatus.APPROVED

        purchase_plan.updated_at = datetime.now(
            timezone.utc,
        )

        return await self.purchase_plan_repository.update(
            purchase_plan,
        )

    def _calculate_item_cost(
        self,
        item: PurchasePlanItemTable,
    ) -> None:

        item.estimated_cost = (
            item.quantity * item.unit_price
        )

    def _calculate_item_costs(
        self,
        items: list[PurchasePlanItemTable],
    ) -> None:

        for item in items:
            self._calculate_item_cost(
                item,
            )

    def _calculate_total_cost(
        self,
        purchase_plan: PurchasePlanTable,
    ) -> None:

        purchase_plan.total_estimated_cost = sum(
            (
                item.estimated_cost
                for item in purchase_plan.items
            ),
            Decimal("0"),
        )

    def _ensure_editable(
        self,
        purchase_plan: PurchasePlanTable,
    ) -> None:

        if purchase_plan.status != PurchasePlanStatus.DRAFT:
            raise ValueError(
                "Only draft purchase plans can be modified.",
            )