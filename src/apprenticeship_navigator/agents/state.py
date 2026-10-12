from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from apprenticeship_navigator.models.postcode import PostcodeLookup


class AgentState(TypedDict):
    """Shared state that every node in the graph reads and updates."""

    messages: Annotated[list[AnyMessage], add_messages]
    postcode: str
    location: PostcodeLookup | None
    location_error: str | None
