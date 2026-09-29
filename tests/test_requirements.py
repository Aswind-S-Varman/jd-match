from jd_match.requirements import extract

STRUCTURED = """Senior Data Engineer

About us:
We are a Series B company building the future of retail analytics.

Requirements:
- 5+ years building pipelines in Python
- Expert SQL, ideally on Snowflake or Databricks
- Production experience with Airflow
- Strong grasp of Kafka for event streaming
- Exposure to Iceberg or Delta Lake is a plus

Responsibilities:
- Own the Looker semantic layer
"""

PROSE = """Backend Developer

We are looking for someone who has worked with Python and SQL before,
and who enjoys building services that scale.
"""


def _texts(extraction):
    return {r.text for r in extraction.requirements}


def test_prose_posting_is_skipped_rather_than_guessed():
    result = extract(PROSE)
    assert result.section_found is False
    assert result.requirements == ()


def test_known_skills_are_recognised():
    skills = {r.skill for r in extract(STRUCTURED).recognised}
    assert {"python", "sql"} <= skills


def test_unknown_terms_are_surfaced_instead_of_dropped():
    unknown = {r.text for r in extract(STRUCTURED).unrecognised}
    assert {"Snowflake", "Databricks", "Airflow", "Kafka", "Iceberg", "Delta Lake"} <= unknown


def test_responsibilities_are_not_treated_as_requirements():
    assert "Looker" not in _texts(extract(STRUCTURED))


def test_prose_and_bare_numbers_are_filtered_out():
    noise = {"5+", "Expert", "Exposure", "Production", "Strong"}
    assert noise.isdisjoint(_texts(extract(STRUCTURED)))


def test_a_plus_marks_a_requirement_optional():
    optional = {r.text for r in extract(STRUCTURED).requirements if r.optional}
    assert "Iceberg" in optional
    assert "Snowflake" not in optional


def test_recognition_reports_how_much_was_understood():
    result = extract(STRUCTURED)
    assert 0.0 < result.recognition < 1.0
    assert len(result.recognised) + len(result.unrecognised) == len(result.requirements)


