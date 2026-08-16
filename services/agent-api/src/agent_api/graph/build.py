from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent_api.graph.nodes import agent_node
from agent_api.graph.state import AgentState
from agent_api.graph.tools import search_products


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode([search_products]))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()
