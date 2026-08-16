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


class EmbeddingError(ShoppingAgentError):
    """Raised when the embedding provider (Voyage) fails - network error, rate
    limit, auth failure, etc. Wraps the underlying provider exception so
    callers depend on our own error type, not a third-party SDK's."""

    def __init__(self, message: str, *, cause: Exception):
        self.cause = cause
        super().__init__(message)
