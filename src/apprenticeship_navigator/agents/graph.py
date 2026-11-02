from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from apprenticeship_navigator.agents.nodes import (
    check_transport,
    explain,
    find_vacancies,
    locate,
    plain_ending,
)
from apprenticeship_navigator.agents.routing import route_after_transport
from apprenticeship_navigator.agents.state import AgentState


def build_graph() -> CompiledStateGraph[Any]:
    """Form-input pipeline: locate, search, check transport, then one of two endings."""
    graph = StateGraph(AgentState)
    graph.add_node("locate", locate)
    graph.add_node("find_vacancies", find_vacancies)
    graph.add_node("check_transport", check_transport)
    graph.add_node("explain", explain)
    graph.add_node("plain_ending", plain_ending)
    graph.add_edge(START, "locate")
    graph.add_edge("locate", "find_vacancies")
    graph.add_edge("find_vacancies", "check_transport")
    graph.add_conditional_edges(
        "check_transport", route_after_transport, ["explain", "plain_ending"]
    )
    graph.add_edge("explain", END)
    graph.add_edge("plain_ending", END)
    return graph.compile()
