import uuid
from datetime import date, datetime, time, timedelta
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command

from apprenticeship_navigator.agents.graph import build_graph
from apprenticeship_navigator.agents.nodes import locate
from apprenticeship_navigator.config import settings

# Classes the checkpointer may rebuild from the database. Any other
# custom class comes back as a plain dictionary (strict mode).
SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("apprenticeship_navigator.sanitise", "SafeLocation"),
        ("apprenticeship_navigator.models.vacancy", "WageType"),
        ("apprenticeship_navigator.models.vacancy", "WageUnit"),
        ("apprenticeship_navigator.models.vacancy", "Vacancy"),
        ("apprenticeship_navigator.models.transport", "VacancyJourney"),
        ("apprenticeship_navigator.models.requirements", "VacancyRequirements"),
        ("apprenticeship_navigator.models.vacancy", "QualificationWeighting"),
    ]
)


def next_weekday_at_nine() -> datetime:
    """Return 09:00 on the next Monday-to-Friday day after today."""
    day = date.today() + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day, time(9, 0))


class NotAwaitingReview(Exception):
    """The run is finished or does not exist, so there is nothing to decide."""


async def start_run(
    postcode: str, distance_in_miles: int
) -> tuple[str, dict[str, Any]]:
    """Start a new run; return its identifier and the graph's result."""
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not set in .env")
    located = await locate(postcode)
    run_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": run_id}}
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url.get_secret_value(), serde=SERDE
    ) as checkpointer:
        await checkpointer.setup()
        graph = build_graph(checkpointer=checkpointer)
        result = await graph.ainvoke(
            {
                "messages": [],
                "location": located["location"],
                "location_error": located["location_error"],
                "distance_in_miles": distance_in_miles,
                "arrive_by": next_weekday_at_nine(),
            },
            config,
        )
    return run_id, result


async def resume_run(run_id: str, decision: str) -> dict[str, Any]:
    """Resume a paused run with the adviser's decision; return the result."""
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not set in .env")
    config: RunnableConfig = {"configurable": {"thread_id": run_id}}
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url.get_secret_value(), serde=SERDE
    ) as checkpointer:
        graph = build_graph(checkpointer=checkpointer)
        snapshot = await graph.aget_state(config)
        if not snapshot.next:
            raise NotAwaitingReview(run_id)
        result = await graph.ainvoke(Command(resume=decision), config)
    return result
