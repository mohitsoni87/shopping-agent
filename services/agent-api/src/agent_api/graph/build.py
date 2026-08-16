from langgraph.graph import END, StateGraph

from agent_api.graph.nodes import embed_node, parse_query, respond, retrieve
from agent_api.graph.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("parse_query", parse_query)
    graph.add_node("embed_query", embed_node)
    graph.add_node("retrieve", retrieve)
    graph.add_node("respond", respond)

    graph.set_entry_point("parse_query")
    graph.add_edge("parse_query", "embed_query")
    graph.add_edge("embed_query", "retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
