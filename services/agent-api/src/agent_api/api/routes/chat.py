from fastapi import APIRouter, Depends
from langgraph.graph.state import CompiledStateGraph
from shopping_agent_common.tenancy import TenantContext

from agent_api.api.dependencies import get_compiled_graph, get_tenant_context
from agent_api.core import get_agent_settings
from agent_api.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    graph: CompiledStateGraph = Depends(get_compiled_graph),
) -> ChatResponse:
    final_state = graph.invoke(
        {"tenant_id": tenant.tenant_id, "env": tenant.env, "user_query": payload.query}
    )
    return ChatResponse(
        search_id=final_state["search_id"],
        answer=final_state["answer"],
        results=final_state["results"],
        offset=0,
        limit=get_agent_settings().search_top_k,
        has_more=final_state["has_more"],
    )
