class ShoppingAgentError(Exception):
    """Base class for domain errors raised anywhere in the shared layer."""


class ProductNotFoundError(ShoppingAgentError):
    def __init__(self, tenant_id: str, env: str, external_product_id: str):
        self.tenant_id = tenant_id
        self.env = env
        self.external_product_id = external_product_id
        super().__init__(
            f"product '{external_product_id}' not found for tenant={tenant_id} env={env}"
        )
