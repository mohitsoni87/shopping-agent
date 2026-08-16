from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from shopping_agent_common.config import get_common_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_common_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def get_session() -> Iterator[Session]:
    """Unit-of-work context manager: commits on clean exit, rolls back on error.
    Prefer this for scripts/CLIs; services should use their own FastAPI
    `Depends`-based session provider so the request lifecycle owns the commit.
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
