from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from agent_api.schemas.product import ProductResult


class AgentState(TypedDict, total=False):
    tenant_id: str
    env: str
    messages: Annotated[list[AnyMessage], add_messages]
    results: list[ProductResult]
    search_id: str
    has_more: bool
