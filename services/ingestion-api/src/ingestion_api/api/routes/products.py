import logging

from fastapi import APIRouter, Depends
from shopping_agent_common.catalog import CatalogService, ProductUpsert
from shopping_agent_common.tenancy import TenantContext

from ingestion_api.api.dependencies import get_catalog_service, get_tenant_context
from ingestion_api.schemas import ProductUpsertResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["products"])


@router.post("/products", response_model=ProductUpsertResponse)
def upsert_product(
    payload: ProductUpsert,
    tenant: TenantContext = Depends(get_tenant_context),
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> ProductUpsertResponse:
    logger.info(
        "webhook.products.received external_product_id=%s tenant_id=%s env=%s",
        payload.external_product_id,
        tenant.tenant_id,
        tenant.env,
    )
    product, outcome = catalog_service.upsert_product(tenant.tenant_id, tenant.env, payload)
    return ProductUpsertResponse(
        product_id=str(product.id),
        external_product_id=product.external_product_id,
        outcome=outcome,
    )
