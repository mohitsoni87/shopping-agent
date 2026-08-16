from collections.abc import Iterator

from fastapi import Depends, Header
from shopping_agent_common.catalog import CatalogService
from shopping_agent_common.db.session import get_session_factory
from shopping_agent_common.embeddings import EmbeddingClient, get_embedding_client
from shopping_agent_common.tenancy import ENV_HEADER, TENANT_ID_HEADER, TenantContext
from sqlalchemy.orm import Session


def get_db_session() -> Iterator[Session]:
    """Request-scoped unit of work: commits when the route handler returns
    cleanly, rolls back on any exception, always closes."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_tenant_context(
    x_tenant_id: str = Header(..., alias=TENANT_ID_HEADER),
    x_env: str = Header(..., alias=ENV_HEADER),
) -> TenantContext:
    return TenantContext(tenant_id=x_tenant_id, env=x_env)


def get_catalog_service(
    session: Session = Depends(get_db_session),
    embedding_client: EmbeddingClient = Depends(get_embedding_client),
) -> CatalogService:
    return CatalogService(session, embedding_client)
