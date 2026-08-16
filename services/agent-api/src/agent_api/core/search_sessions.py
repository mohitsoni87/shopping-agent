import threading
import uuid
from dataclasses import dataclass
from functools import lru_cache

from cachetools import TTLCache
from shopping_agent_common.product_types import Gender
from shopping_agent_common.repositories import ItemFilters


@dataclass(frozen=True, slots=True)
class SearchSession:
    """The parsed, embedded query behind one chat turn. Cached so that
    paginating past the first page re-runs only the cheap DB query - not the
    LLM query-parse or the Voyage embed call."""

    tenant_id: str
    env: str
    query_embedding: list[float]
    item_filters: ItemFilters
    category: str | None
    gender: Gender | None


class SearchSessionStore:
    """Short-lived, in-process cache from search_id to SearchSession.

    In-process and TTL-bound is the right tradeoff for a single-replica
    prototype - a session that expires just means "next" re-runs the chat
    query instead of paginating. Swap for Redis if agent-api ever runs more
    than one replica.
    """

    def __init__(self, maxsize: int = 1000, ttl_seconds: int = 600):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        self._lock = threading.Lock()

    def create(self, session: SearchSession) -> str:
        search_id = uuid.uuid4().hex
        with self._lock:
            self._cache[search_id] = session
        return search_id

    def get(self, search_id: str) -> SearchSession | None:
        with self._lock:
            return self._cache.get(search_id)


@lru_cache
def get_search_session_store() -> SearchSessionStore:
    return SearchSessionStore()
