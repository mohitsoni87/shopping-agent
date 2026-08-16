from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import Field
from shopping_agent_common.db import get_session
from shopping_agent_common.embeddings import get_embedding_client
from shopping_agent_common.product_types import Gender
from shopping_agent_common.repositories import ItemFilters
from shopping_agent_common.search import SearchService

from agent_api.core import SearchSession, get_agent_settings, get_search_session_store
from agent_api.serializers import serialize_product_matches

_settings = get_agent_settings()


@tool
def search_products(
    semantic_query: Annotated[
        str,
        Field(
            description="The product itself the shopper is looking for, rewritten as a "
            "short search phrase (no size/color/price constraints), e.g. "
            "'red wool jacket for fall'."
        ),
    ],
    size: Annotated[str | None, Field(description="Requested size, if mentioned.")] = None,
    color: Annotated[str | None, Field(description="Requested color, if mentioned.")] = None,
    category: Annotated[
        str | None,
        Field(
            description="Product category, ONLY if it exactly matches one of the categories "
            "listed in the system prompt. Leave null otherwise - the semantic search "
            "already covers product type."
        ),
    ] = None,
    gender: Annotated[
        Gender | None,
        Field(
            description="Target gender, ONLY if the shopper explicitly said 'men's'/'for "
            "men'/'women's'/'for women'/'unisex' or similar. Leave null if gender wasn't "
            "mentioned - do not infer it from the product type alone (e.g. a request for "
            "'a dress' does not imply gender='women')."
        ),
    ] = None,
    price_min: Annotated[float | None, Field(description="Minimum price, if mentioned.")] = None,
    price_max: Annotated[float | None, Field(description="Maximum price, if mentioned.")] = None,
    tenant_id: Annotated[str, InjectedState("tenant_id")] = "",
    env: Annotated[str, InjectedState("env")] = "",
    tool_call_id: Annotated[str, InjectedToolCallId] = "",
) -> Command:
    """Search the tenant's product catalog for items matching the shopper's request. Call
    this whenever the shopper is asking to find, browse, or search for a product - do NOT
    call this for greetings, thanks, or unrelated chit-chat."""
    item_filters = ItemFilters(size=size, color=color, price_min=price_min, price_max=price_max)
    query_embedding = get_embedding_client().embed_query(semantic_query)

    with get_session() as session:
        page = SearchService(session).search_products(
            tenant_id=tenant_id,
            env=env,
            query_embedding=query_embedding,
            item_filters=item_filters,
            category=category,
            gender=gender,
            limit=_settings.search_top_k,
        )
        results = serialize_product_matches(page.matches)

    search_id = get_search_session_store().create(
        SearchSession(
            tenant_id=tenant_id,
            env=env,
            query_embedding=query_embedding,
            item_filters=item_filters,
            category=category,
            gender=gender,
        )
    )

    tool_message = ToolMessage(
        content=f"Found {len(results)} matching product(s). They will be shown to the "
        "shopper as visual cards - do not list them in your reply.",
        tool_call_id=tool_call_id,
    )
    return Command(
        update={
            "results": results,
            "search_id": search_id,
            "has_more": page.has_more,
            "messages": [tool_message],
        }
    )
