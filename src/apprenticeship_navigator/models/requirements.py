from pydantic import BaseModel

from apprenticeship_navigator.models.vacancy import VacancyQualification


class VacancyRequirements(BaseModel):
    """What one advert asks of an applicant, kept apart from contact details."""

    reference: str
    qualifications: list[VacancyQualification] = []
    skills: list[str] = []
    things_to_consider: str | None = None
