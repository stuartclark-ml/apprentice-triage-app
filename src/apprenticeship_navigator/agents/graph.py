from typing import Any

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from apprenticeship_navigator.agents.state import AgentState
from apprenticeship_navigator.config import settings
from apprenticeship_navigator.tools.vacancy import search_apprenticeship_vacancies

SYSTEM_PROMPT = (
    "You help people in England find apprenticeship vacancies. "
    "When the user gives a postcode, use the search tool. "
    "Only report vacancies the tool returned; never invent any. "
    "If no postcode is given, ask for one."
)

TOOLS = [search_apprenticeship_vacancies]


def build_graph() -> CompiledStateGraph[Any]:
    """Build the agent-and-tools loop. Requires GOOGLE_API_KEY."""
    if settings.google_api_key is None:
        raise RuntimeError("GOOGLE_API_KEY is not set. Add it to .env.")

    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
    ).bind_tools(TOOLS)

    async def agent(state: AgentState) -> dict[str, list[BaseMessage]]:
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = await model.ainvoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS, handle_tool_errors=True))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()
