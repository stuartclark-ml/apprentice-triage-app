from apprenticeship_navigator.models.requirements import html_to_text


def test_html_to_text_turns_lists_into_lines():
    raw = (
        "<p>Eligibility&nbsp;</p><ul><li>Right to work in the UK&nbsp;</li>"
        "<li>UK resident for 3 years</li></ul>"
    )
    assert html_to_text(raw) == (
        "Eligibility\n- Right to work in the UK\n- UK resident for 3 years"
    )


def test_html_to_text_empty_values_become_none():
    assert html_to_text(None) is None
    assert html_to_text("<p>&nbsp;</p>") is None


def test_html_to_text_removes_invisible_spaces():
    assert html_to_text("<p>\u200b\u200bInfrastructure</p>") == "Infrastructure"
