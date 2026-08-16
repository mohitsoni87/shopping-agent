import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from shopping_agent_common.search import SearchService
from sqlalchemy.orm import Session

from agent_api.api.dependencies import get_db_session
from agent_api.core import SearchSessionStore, get_search_session_store
from agent_api.schemas import SearchPageResponse
from agent_api.serializers import serialize_product_matches

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.get("/search/{search_id}", response_model=SearchPageResponse)
def get_search_page(
    search_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=50),
    session: Session = Depends(get_db_session),
    store: SearchSessionStore = Depends(get_search_session_store),
) -> SearchPageResponse:
    search_session = store.get(search_id)
    if search_session is None:
        logger.warning("search.page_requested search_id=%s not_found_or_expired", search_id)
        raise HTTPException(status_code=404, detail="Search session not found or expired")

    logger.info(
        "search.page_requested search_id=%s tenant_id=%s env=%s offset=%d limit=%d",
        search_id,
        search_session.tenant_id,
        search_session.env,
        offset,
        limit,
    )
    page = SearchService(session).search_products(
        tenant_id=search_session.tenant_id,
        env=search_session.env,
        query_embedding=search_session.query_embedding,
        item_filters=search_session.item_filters,
        category=search_session.category,
        gender=search_session.gender,
        limit=limit,
        offset=offset,
    )
    return SearchPageResponse(
        results=serialize_product_matches(page.matches),
        offset=page.offset,
        limit=page.limit,
        has_more=page.has_more,
    )
