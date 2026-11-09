import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from apprenticeship_navigator.agents import graph as graph_module

CONFIG = {"configurable": {"thread_id": "test-run"}}


async def fake_find_vacancies(state):
    return {"vacancies": []}


async def fake_check_transport(state):
    return {"vacancy_journeys": [], "transport_status": "ok"}


async def fake_explain(state):
    return {"explanation": "Gemini's text."}


@pytest.fixture
def app(monkeypatch):
    """The real graph, with every step before review replaced by a fake."""
    monkeypatch.setattr(graph_module, "find_vacancies", fake_find_vacancies)
    monkeypatch.setattr(graph_module, "check_transport", fake_check_transport)
    monkeypatch.setattr(graph_module, "route_after_transport", lambda state: "explain")
    monkeypatch.setattr(graph_module, "explain", fake_explain)
    return graph_module.build_graph(checkpointer=InMemorySaver())


@pytest.mark.asyncio
async def test_run_pauses_with_explanation_for_review(app):
    result = await app.ainvoke({"distance_in_miles": 10}, CONFIG)
    assert result["__interrupt__"][0].value["explanation"] == "Gemini's text."


@pytest.mark.asyncio
async def test_approve_keeps_gemini_text(app):
    await app.ainvoke({"distance_in_miles": 10}, CONFIG)
    result = await app.ainvoke(Command(resume="approve"), CONFIG)
    assert result["explanation"] == "Gemini's text."
    assert "__interrupt__" not in result


@pytest.mark.asyncio
async def test_reject_withholds_gemini_text(app):
    await app.ainvoke({"distance_in_miles": 10}, CONFIG)
    result = await app.ainvoke(Command(resume="reject"), CONFIG)
    assert result["explanation"].startswith("Explanation withheld")


@pytest.mark.asyncio
async def test_unknown_decision_raises(app):
    await app.ainvoke({"distance_in_miles": 10}, CONFIG)
    with pytest.raises(ValueError):
        await app.ainvoke(Command(resume="looks fine"), CONFIG)
