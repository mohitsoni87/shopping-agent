from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from shopping_agent_common.db import get_session
from shopping_agent_common.repositories import ProductRepository

from agent_api.core import get_agent_settings
from agent_api.graph.prompts import AGENT_SYSTEM_PROMPT
from agent_api.graph.state import AgentState
from agent_api.graph.tools import search_products

_settings = get_agent_settings()
_llm = ChatAnthropic(model=_settings.claude_model, api_key=_settings.anthropic_api_key)
_llm_with_tools = _llm.bind_tools([search_products])


def agent_node(state: AgentState) -> dict:
    with get_session() as session:
        categories = ProductRepository(session).list_categories(state["tenant_id"], state["env"])
    categories_text = ", ".join(categories) if categories else "(none known yet)"

    system_message = SystemMessage(content=AGENT_SYSTEM_PROMPT.format(categories=categories_text))
    response = _llm_with_tools.invoke([system_message, *state["messages"]])
    return {"messages": [response]}
