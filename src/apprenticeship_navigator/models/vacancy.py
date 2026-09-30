from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class WageType(str, Enum):
    apprenticeship_minimum = "ApprenticeshipMinimum"
    national_minimum = "NationalMinimum"
    custom = "Custom"
    competitive_salary = "CompetitiveSalary"


class WageUnit(str, Enum):
    unspecified = "Unspecified"
    weekly = "Weekly"
    monthly = "Monthly"
    annually = "Annually"


class QualificationWeighting(str, Enum):
    essential = "Essential"
    desired = "Desired"


class CamelModel(BaseModel):
    """Base for models whose incoming data uses camelCase keys."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class VacancyWage(CamelModel):
    wage_type: WageType | None = None
    wage_amount: float | None = None
    wage_unit: WageUnit | None = None
    wage_additional_information: str | None = None
    working_week_description: str | None = None


class VacancyAddress(CamelModel):
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    address_line4: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class VacancyCourse(CamelModel):
    lars_code: int | None = None
    title: str | None = None
    level: int | None = None
    route: str | None = None
    type: str | None = None


class VacancyQualification(CamelModel):
    weighting: QualificationWeighting | None = None
    qualification_type: str | None = None
    subject: str | None = None
    grade: str | None = None


class Vacancy(CamelModel):
    title: str | None = None
    description: str | None = None
    number_of_positions: int | None = None
    posted_date: datetime | None = None
    closing_date: datetime | None = None
    start_date: datetime | None = None
    wage: VacancyWage | None = None
    hours_per_week: float | None = None
    expected_duration: str | None = None
    addresses: list[VacancyAddress] | None = None
    application_url: str | None = None
    distance: float | None = None
    employer_name: str | None = None
    employer_website_url: str | None = None
    employer_contact_name: str | None = None
    employer_contact_phone: str | None = None
    employer_contact_email: str | None = None
    course: VacancyCourse | None = None
    apprenticeship_level: str | None = None
    provider_name: str | None = None
    ukprn: int | None = None
    is_disability_confident: bool | None = None
    vacancy_url: str | None = None
    vacancy_reference: str | None = None
    is_national_vacancy: bool | None = None
    is_national_vacancy_details: str | None = None
    employer_description: str | None = None
    training_description: str | None = None
    additional_training_description: str | None = None
    outcome_description: str | None = None
    full_description: str | None = None
    skills: list[str] | None = None
    qualifications: list[VacancyQualification] | None = None
    things_to_consider: str | None = None
    company_benefits_information: str | None = None


class VacancySearchResponse(CamelModel):
    total: int | None = None
    total_filtered: int | None = None
    total_pages: int | None = None
    vacancies: list[Vacancy] = []
