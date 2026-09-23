from jd_match.keywords import find_skills, normalize


def test_aliases_resolve_to_canonical_names():
    assert "javascript" in find_skills("Strong JS experience")
    assert "node.js" in find_skills("Built services in NodeJS")
    assert "kubernetes" in find_skills("Deployed to k8s")


def test_symbols_in_skill_names_survive_normalization():
    assert "c++" in find_skills("Wrote C++ for embedded systems")
    assert "ci/cd" in find_skills("Owned the CI/CD pipeline")
    assert "c#" in find_skills("Maintained a C# service")


def test_substrings_do_not_create_false_matches():
    assert "java" not in find_skills("Comfortable with JavaScript")
    assert find_skills("I am going to Google") == set()


def test_normalize_pads_text_for_boundary_matching():
    assert normalize("Python, SQL") == " python sql "


