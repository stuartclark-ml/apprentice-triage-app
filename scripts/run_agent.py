import asyncio
import sys
from datetime import date, datetime, time, timedelta

from apprenticeship_navigator.agents.graph import build_graph

from apprenticeship_navigator.agents.nodes import locate


def next_weekday_at_nine() -> datetime:
    """Return 09:00 on the next Monday-to-Friday day after today."""
    day = date.today() + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return datetime.combine(day, time(9, 0))


async def main(postcode: str) -> None:
    located = await locate(postcode)
    graph = build_graph()
    result = await graph.ainvoke(
        {
            "messages": [],
            "location": located["location"],
            "location_error": located["location_error"],
            "distance_in_miles": 10,
            "arrive_by": next_weekday_at_nine(),
        }
    )
    print(f"Transport status: {result['transport_status']}")
    for record in result["vacancy_journeys"]:
        print(f"  {record.feasibility}: {record.vacancy.title}")
    print(result["explanation"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(
            "Error: no postcode given. Usage: uv run python scripts/run_agent.py POSTCODE (for example SW1A1AA)"
        )
    asyncio.run(main(sys.argv[1]))
