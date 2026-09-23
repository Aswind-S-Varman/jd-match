from jd_match.matcher import compare


def test_coverage_counts_only_required_skills():
    result = compare("Python and SQL", "We need Python, SQL and Docker")

    assert result.matched == ["python", "sql"]
    assert result.missing == ["docker"]
    assert result.required_count == 3
    assert result.coverage == 2 / 3


def test_extra_skills_are_reported_separately():
    result = compare("Python and Terraform experience", "We need Python")

    assert result.missing == []
    assert "terraform" in result.extra


def test_empty_job_description_gives_zero_coverage():
    assert compare("Python", "").coverage == 0.0


