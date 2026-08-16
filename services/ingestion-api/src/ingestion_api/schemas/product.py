from pydantic import BaseModel


class ProductUpsertResponse(BaseModel):
    product_id: str
    external_product_id: str
