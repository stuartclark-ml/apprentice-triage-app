import html
import re
from pydantic import BaseModel

from apprenticeship_navigator.models.vacancy import VacancyQualification


class VacancyRequirements(BaseModel):
    """What one advert asks of an applicant, kept apart from contact details."""

    reference: str
    qualifications: list[VacancyQualification] = []
    skills: list[str] = []
    things_to_consider: str | None = None


def html_to_text(raw: str | None) -> str | None:
    """Turn advert HTML into plain lines; list items start with '- '. Blank becomes None."""
    if raw is None:
        return None
    text = re.sub(r"<li[^>]*>", "- ", raw)
    text = re.sub(r"<br\s*/?>|</p>|</li>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\xa0", " ").replace("\u200b", "")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned or None
