"""Build the applicant view from a run's result. Formatting happens here."""

from apprenticeship_navigator.models.vacancy import VacancyWage, WageType, WageUnit

WAGE_TYPE_WORDS = {
    WageType.apprenticeship_minimum: "Apprenticeship minimum wage",
    WageType.national_minimum: "National minimum wage",
    WageType.competitive_salary: "Competitive salary",
}
UNIT_WORDS = {
    WageUnit.weekly: " a week",
    WageUnit.monthly: " a month",
    WageUnit.annually: " a year",
}


def wage_text(wage: VacancyWage | None) -> str | None:
    """One line of wage, never inventing a figure the advert did not give."""
    if wage is None:
        return None
    if wage.wage_type == WageType.custom and wage.wage_amount is not None:
        unit = UNIT_WORDS.get(wage.wage_unit, "") if wage.wage_unit else ""
        return f"£{wage.wage_amount:,.2f}{unit}"
    parts = []
    if wage.wage_type in WAGE_TYPE_WORDS:
        parts.append(WAGE_TYPE_WORDS[wage.wage_type])
    if wage.wage_additional_information:
        parts.append(wage.wage_additional_information.strip())
    return ". ".join(parts) or None
