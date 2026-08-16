import logging

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from shopping_agent_common.tenancy import TenantContext

from agent_api.api.dependencies import get_compiled_graph, get_tenant_context
from agent_api.core import get_agent_settings
from agent_api.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    graph: CompiledStateGraph = Depends(get_compiled_graph),
) -> ChatResponse:
    logger.info(
        "chat.received tenant_id=%s env=%s query=%r", tenant.tenant_id, tenant.env, payload.query
    )
    final_state = graph.invoke(
        {
            "tenant_id": tenant.tenant_id,
            "env": tenant.env,
            "messages": [HumanMessage(content=payload.query)],
        }
    )
    search_id = final_state.get("search_id")
    results = final_state.get("results", [])
    logger.info(
        "chat.responded tenant_id=%s env=%s searched=%s result_count=%d",
        tenant.tenant_id,
        tenant.env,
        search_id is not None,
        len(results),
    )
    return ChatResponse(
        answer=final_state["messages"][-1].content,
        search_id=search_id,
        results=results,
        offset=0,
        limit=get_agent_settings().search_top_k,
        has_more=final_state.get("has_more", False),
    )
