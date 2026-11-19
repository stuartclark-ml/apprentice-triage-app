import asyncio
import sys
import json

from apprenticeship_navigator.models.requirements import VacancyRequirements
from apprenticeship_navigator.models.vacancy import QualificationWeighting
from apprenticeship_navigator.models.transport import Journey
from apprenticeship_navigator.runs import resume_run, start_run


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
    run_id, result = await start_run(postcode, distance_in_miles=10)
    show(result, run_id)


async def resume(run_id: str, decision: str) -> None:
    result = await resume_run(run_id, decision)
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
