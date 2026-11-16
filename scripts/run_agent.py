import asyncio
import sys
import json
import uuid

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from langchain_core.runnables import RunnableConfig

from apprenticeship_navigator.config import settings
from apprenticeship_navigator.agents.graph import build_graph
from apprenticeship_navigator.agents.nodes import locate
from apprenticeship_navigator.models.requirements import VacancyRequirements
from apprenticeship_navigator.models.vacancy import QualificationWeighting
from apprenticeship_navigator.models.transport import Journey
from apprenticeship_navigator.runs import SERDE, next_weekday_at_nine


def show_route(journey: Journey | None) -> None:
    """Print the fastest journey's leaving time, legs and fare, if there is one."""
    if journey is None:
        return
    legs = ", then ".join(f"{leg.mode.name} {leg.duration} min" for leg in journey.legs)
    print(f"    Route: leave {journey.start_date_time:%H:%M}, {legs}")
    if journey.fare is not None and journey.fare.total_cost is not None:
        print(f"    Fare: £{journey.fare.total_cost / 100:.2f}")


MAX_CONSIDER_LINES = 8


def show_requirements(requirements: VacancyRequirements | None) -> None:
    """Print one advert's requirements, or say they could not be fetched."""
    if requirements is None:
        print("    Requirements: details unavailable")
        return
    for q in requirements.qualifications:
        label = (
            "Must have"
            if q.weighting == QualificationWeighting.essential
            else "Nice to have"
        )
        print(f"    {label}: {q.qualification_type} {q.subject} ({q.grade})")
    if requirements.skills:
        print(f"    Skills: {', '.join(requirements.skills)}")
    if requirements.things_to_consider:
        lines = requirements.things_to_consider.splitlines()
        print("    Things to consider:")
        for line in lines[:MAX_CONSIDER_LINES]:
            print(f"      {line}")
        if len(lines) > MAX_CONSIDER_LINES:
            print("      ... (see the full advert)")


def show(result: dict, run_id: str) -> None:
    """Print the journeys, then either the pause for review or the final text."""
    print(f"Transport status: {result['transport_status']}")
    found = result.get("requirements", {})
    for record in result["vacancy_journeys"]:
        print(f"  {record.feasibility}: {record.vacancy.title}")
        show_route(record.journey)
        show_requirements(found.get(record.vacancy.vacancy_reference or ""))
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
