from typing import Any

from apprenticeship_navigator.models.vacancy import VacancySearchResponse, VacancyWage
from apprenticeship_navigator.tools.vacancy import _summarise, _wage_text


def test_summarise_shows_wage_text_and_rounded_distance(
    vacancy_search_payload: dict[str, Any],
) -> None:
    vacancy = VacancySearchResponse.model_validate(vacancy_search_payload).vacancies[0]
    line = _summarise(vacancy)
    assert "£14,976 a year" in line
    assert "6.7 miles" in line
    assert "wage not stated" not in line


def test_wage_text_prefers_numeric_amount_when_present() -> None:
    # Not a captured shape: exercises the branch a Custom wage would take.
    wage = VacancyWage.model_validate({"wageAmount": 17082, "wageUnit": "Annually"})
    assert _wage_text(wage) == "£17,082 annually"


def test_wage_text_falls_back_when_nothing_is_stated() -> None:
    assert _wage_text(None) == "wage not stated"
    assert _wage_text(VacancyWage()) == "wage not stated"
