from apprenticeship_navigator.models.vacancy import (
    Vacancy,
    VacancySearchResponse,
    WageType,
)

from typing import Any


def test_vacancy_reads_camel_case_top_level_field() -> None:
    vacancy = Vacancy.model_validate({"employerName": "Acme Engineering"})
    assert vacancy.employer_name == "Acme Engineering"


def test_vacancy_reads_camel_case_nested_field() -> None:
    vacancy = Vacancy.model_validate({"wage": {"wageType": "ApprenticeshipMinimum"}})
    assert vacancy.wage is not None
    assert vacancy.wage.wage_type == WageType.apprenticeship_minimum


def test_vacancy_reads_camel_case_field_inside_list() -> None:
    vacancy = Vacancy.model_validate({"addresses": [{"addressLine1": "1 High Street"}]})
    assert vacancy.addresses is not None
    assert vacancy.addresses[0].address_line1 == "1 High Street"


def test_search_response_reads_camel_case_totals() -> None:
    response = VacancySearchResponse.model_validate({"totalFiltered": 7})
    assert response.total_filtered == 7


def test_search_response_parses_real_apprenticeship_minimum_wage(
    vacancy_search_payload: dict[str, Any],
) -> None:
    response = VacancySearchResponse.model_validate(vacancy_search_payload)
    wage = response.vacancies[0].wage
    assert wage is not None
    assert wage.wage_type == WageType.apprenticeship_minimum
    assert wage.wage_amount is None
    assert wage.wage_additional_information == "£14,976 a year"
