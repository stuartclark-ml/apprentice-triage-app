from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver

from apprenticeship_navigator.agents.nodes import (
    check_transport,
    explain,
    find_vacancies,
    plain_ending,
    review,
)
from apprenticeship_navigator.agents.routing import route_after_transport
from apprenticeship_navigator.agents.state import AgentState


def build_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph[Any]:
    """Form-input pipeline: search, check transport, then one of two endings.

    The explanation ending pauses for a careers adviser's review.
    With a checkpointer, state is saved after every step, so a run can pause and resume.
    """
    graph = StateGraph(AgentState)
    graph.add_node("find_vacancies", find_vacancies)
    graph.add_node("check_transport", check_transport)
    graph.add_node("explain", explain)
    graph.add_node("plain_ending", plain_ending)
    graph.add_node("review", review)
    graph.add_edge(START, "find_vacancies")
    graph.add_edge("find_vacancies", "check_transport")
    graph.add_conditional_edges(
        "check_transport", route_after_transport, ["explain", "plain_ending"]
    )
    graph.add_edge("explain", "review")
    graph.add_edge("review", END)
    graph.add_edge("plain_ending", END)
    return graph.compile(checkpointer=checkpointer)
