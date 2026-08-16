from collections.abc import Iterator
from functools import lru_cache

from fastapi import Header
from langgraph.graph.state import CompiledStateGraph
from shopping_agent_common.db.session import get_session_factory
from shopping_agent_common.tenancy import ENV_HEADER, TENANT_ID_HEADER, TenantContext
from sqlalchemy.orm import Session

from agent_api.graph import build_graph


@lru_cache
def get_compiled_graph() -> CompiledStateGraph:
    return build_graph()


def get_db_session() -> Iterator[Session]:
    """Request-scoped unit of work for routes that talk to the DB directly
    (the search-pagination route) rather than through the graph."""
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
