from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
from shopping_agent_common.db import get_session
from shopping_agent_common.embeddings import get_embedding_client
from shopping_agent_common.repositories import ItemFilters, ProductRepository
from shopping_agent_common.search import SearchService

from agent_api.core import SearchSession, get_agent_settings, get_search_session_store
from agent_api.graph.state import AgentState
from agent_api.serializers import serialize_product_matches

_settings = get_agent_settings()
_llm = ChatAnthropic(model=_settings.claude_model, api_key=_settings.anthropic_api_key)


class ParsedQuery(BaseModel):
    semantic_query: str = Field(
        description="The product itself the shopper is looking for, rewritten as a short "
        "search phrase (no size/color/price constraints), e.g. 'red wool jacket for fall'."
    )
    size: str | None = Field(default=None, description="Requested size, if mentioned.")
    color: str | None = Field(default=None, description="Requested color, if mentioned.")
    category: str | None = Field(
        default=None,
        description="Product category, ONLY if it exactly matches one of the categories "
        "given in the prompt. Leave null if no listed category clearly applies - "
        "the semantic search already covers product type.",
    )
    price_min: float | None = Field(default=None, description="Minimum price, if mentioned.")
    price_max: float | None = Field(default=None, description="Maximum price, if mentioned.")


_parser_llm = _llm.with_structured_output(ParsedQuery)

PARSE_PROMPT = (
    "Extract a product search from this shopper query. Split out the semantic description "
    "of the product from any explicit size, color, category, or price constraints.\n\n"
    "Known product categories for this store: {categories}\n"
    "Only set `category` to one of these exact values, or leave it null.\n\n"
    "Query: {query}"
)

RESPOND_PROMPT = (
    "You are a shopping assistant for an e-commerce storefront. The shopper asked: {query}\n\n"
    "{result_count} matching product(s) will be shown directly below your reply as visual "
    "product cards (image, title, price, colors) - do NOT list product names, prices, sizes, "
    "or colors in your reply, that information is already visible in the cards.\n\n"
    "Write exactly one short, professional sentence introducing the results - or, if "
    "result_count is 0, say plainly that nothing matched and suggest broadening the search. "
    "No greeting, no emojis, no exclamation points."
)


def parse_query(state: AgentState) -> dict:
    with get_session() as session:
        categories = ProductRepository(session).list_categories(state["tenant_id"], state["env"])

    categories_text = ", ".join(categories) if categories else "(none known yet)"
    parsed = _parser_llm.invoke(
        PARSE_PROMPT.format(categories=categories_text, query=state["user_query"])
    )
    return {
        "semantic_query": parsed.semantic_query,
        "size": parsed.size,
        "color": parsed.color,
        "category": parsed.category,
        "price_min": parsed.price_min,
        "price_max": parsed.price_max,
    }


def embed_node(state: AgentState) -> dict:
    return {"query_embedding": get_embedding_client().embed_query(state["semantic_query"])}


def retrieve(state: AgentState) -> dict:
    item_filters = ItemFilters(
        size=state.get("size"),
        color=state.get("color"),
        price_min=state.get("price_min"),
        price_max=state.get("price_max"),
    )
    with get_session() as session:
        page = SearchService(session).search_products(
            tenant_id=state["tenant_id"],
            env=state["env"],
            query_embedding=state["query_embedding"],
            item_filters=item_filters,
            category=state.get("category"),
            limit=_settings.search_top_k,
        )
        results = serialize_product_matches(page.matches)

    search_id = get_search_session_store().create(
        SearchSession(
            tenant_id=state["tenant_id"],
            env=state["env"],
            query_embedding=state["query_embedding"],
            item_filters=item_filters,
            category=state.get("category"),
        )
    )
    return {"results": results, "search_id": search_id, "has_more": page.has_more}


def respond(state: AgentState) -> dict:
    reply = _llm.invoke(
        RESPOND_PROMPT.format(query=state["user_query"], result_count=len(state["results"]))
    )
    return {"answer": reply.content}
