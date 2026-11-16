from apprenticeship_navigator.models.vacancy import VacancyWage, WageType, WageUnit
from apprenticeship_navigator.web.views import wage_text


def test_custom_wage_without_amount_shows_advert_text() -> None:
    wage = VacancyWage(
        wage_type=WageType.custom,
        wage_unit=WageUnit.annually,
        wage_additional_information="£21,263 a year",
    )
    assert wage_text(wage) == "£21,263 a year"


def test_custom_wage_with_amount_is_formatted() -> None:
    wage = VacancyWage(
        wage_type=WageType.custom, wage_amount=15704, wage_unit=WageUnit.annually
    )
    assert wage_text(wage) == "£15,704.00 a year"


def test_minimum_wage_never_invents_a_figure() -> None:
    text = wage_text(VacancyWage(wage_type=WageType.apprenticeship_minimum))
    assert text == "Apprenticeship minimum wage"
    assert "£" not in text


def test_wage_words_and_advert_text_are_joined() -> None:
    wage = VacancyWage(
        wage_type=WageType.apprenticeship_minimum,
        wage_additional_information="  Plus travel costs ",
    )
    assert wage_text(wage) == "Apprenticeship minimum wage. Plus travel costs"


def test_no_wage_gives_none() -> None:
    assert wage_text(None) is None
