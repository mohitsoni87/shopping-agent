from pydantic import BaseModel
from shopping_agent_common.catalog import UpsertOutcome


class ProductUpsertResponse(BaseModel):
    product_id: str
    external_product_id: str
    outcome: UpsertOutcome
