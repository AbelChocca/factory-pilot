from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import logger
from app.core.pydantic_settings import settings
from app.core.middlewares.manager import init_middlewares
from app.db.config import init_db

from app.features.materials.material_route import material_router
from app.features.inventory.inventory_routes import inventory_movement_router
from app.features.products.product_route import product_router
from app.features.suppliers.supplier_router import supplier_router
from app.features.suppliers.supplier_material_router import supplier_material_router
from app.features.products.product_material_route import product_material_router
from app.ai.rag.rag_router import rag_router
from app.ai.chat.chat_router import chat_router
from app.features.production_risk.router.production_risk import production_risk_router
from app.features.production_risk.router.material_impact import material_impact_router
from app.features.purchase_plans.purchase_plan_router import purchase_plan_router
from app.features.dashboard.dashboard_route import dashboard_route

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting FactoryPilot API")

    try:
        await init_db()
        logger.info("✅ Database connected")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

    yield

    logger.info("🛑 Shutting down FactoryPilot API")

is_prod = settings.ENV == "production"


app = FastAPI(
    title="FactoryPilot API",
    description=(
        "AI Copilot for manufacturing operations "
        "with inventory intelligence."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if is_prod else "/docs",
    redoc_url=None if is_prod else "/redoc",
    openapi_url=None if is_prod else "/openapi.json",
)


init_middlewares(app)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Routers
app.include_router(material_router)
app.include_router(inventory_movement_router)
app.include_router(product_router)
app.include_router(supplier_router)
app.include_router(supplier_material_router)
app.include_router(product_material_router)
app.include_router(rag_router)
app.include_router(chat_router)
app.include_router(production_risk_router)
app.include_router(material_impact_router)
app.include_router(purchase_plan_router)
app.include_router(dashboard_route)