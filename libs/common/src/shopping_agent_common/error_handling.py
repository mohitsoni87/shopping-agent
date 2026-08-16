import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shopping_agent_common.exceptions import EmbeddingError
from shopping_agent_common.tenancy import ENV_HEADER, TENANT_ID_HEADER

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """App-wide handlers so every unhandled exception is logged server-side
    with request context, and clients never receive a raw traceback. Shared
    across services so both get identical, consistent error responses."""

    @app.exception_handler(EmbeddingError)
    async def handle_embedding_error(request: Request, exc: EmbeddingError) -> JSONResponse:
        logger.error(
            "EmbeddingError on %s %s tenant_id=%s env=%s: %s",
            request.method,
            request.url.path,
            request.headers.get(TENANT_ID_HEADER),
            request.headers.get(ENV_HEADER),
            exc,
        )
        return JSONResponse(
            status_code=503,
            content={
                "detail": "The embedding service is temporarily unavailable. "
                "Please try again shortly."
            },
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception on %s %s tenant_id=%s env=%s",
            request.method,
            request.url.path,
            request.headers.get(TENANT_ID_HEADER),
            request.headers.get(ENV_HEADER),
            exc_info=exc,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})
