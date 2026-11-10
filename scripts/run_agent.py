import asyncio
import sys
import json
import uuid

from datetime import date, datetime, time, timedelta
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command

from langchain_core.runnables import RunnableConfig

from apprenticeship_navigator.config import settings
from apprenticeship_navigator.agents.graph import build_graph
from apprenticeship_navigator.agents.nodes import locate

# Classes the checkpointer may rebuild from the database. Any other
# custom class comes back as a plain dictionary (strict mode).
SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("apprenticeship_navigator.sanitise", "SafeLocation"),
        ("apprenticeship_navigator.models.vacancy", "WageType"),
        ("apprenticeship_navigator.models.vacancy", "WageUnit"),
        ("apprenticeship_navigator.models.vacancy", "Vacancy"),
        ("apprenticeship_navigator.models.transport", "VacancyJourney"),
    ]
)


def next_weekday_at_nine() -> datetime:
    """Return 09:00 on the next Monday-to-Friday day after today."""
    day = date.today() + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day, time(9, 0))


def show(result: dict, run_id: str) -> None:
    """Print the journeys, then either the pause for review or the final text."""
    print(f"Transport status: {result['transport_status']}")
    for record in result["vacancy_journeys"]:
        print(f"  {record.feasibility}: {record.vacancy.title}")
    if "__interrupt__" in result:
        pause = result["__interrupt__"][0].value
        print(
            f"\nAwaiting careers adviser review.\nExplanation: {pause['explanation']}"
        )
        print(f"Source facts: {json.dumps(pause['facts'], indent=2)}")
        print(f"\nResume with: resume {run_id} approve (or reject)")
    else:
        print(result["explanation"])


async def start(postcode: str) -> None:
    if settings.database_url is None:
        sys.exit("Error: DATABASE_URL is not set in .env")
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
                "distance_in_miles": 10,
                "arrive_by": next_weekday_at_nine(),
            },
            config,
        )
    show(result, run_id)


async def resume(run_id: str, decision: str) -> None:
    if settings.database_url is None:
        sys.exit("Error: DATABASE_URL is not set in .env")
    config: RunnableConfig = {"configurable": {"thread_id": run_id}}
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url.get_secret_value(), serde=SERDE
    ) as checkpointer:
        graph = build_graph(checkpointer=checkpointer)
        result = await graph.ainvoke(Command(resume=decision), config)
    show(result, run_id)


if __name__ == "__main__":
    usage = (
        "Usage: uv run python scripts/run_agent.py start POSTCODE\n"
        "   or: uv run python scripts/run_agent.py resume RUN_ID approve|reject"
    )
    if len(sys.argv) == 3 and sys.argv[1] == "start":
        asyncio.run(start(sys.argv[2]))
    elif (
        len(sys.argv) == 4
        and sys.argv[1] == "resume"
        and sys.argv[3] in ("approve", "reject")
    ):
        asyncio.run(resume(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(usage)
