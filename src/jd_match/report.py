from .ats_checks import Issue
from .matcher import MatchResult


def render(result: MatchResult, issues: list[Issue]) -> str:
    lines = [
        "RESUME vs JOB DESCRIPTION",
        "=" * 48,
        "",
        f"Coverage: {result.coverage:.0%} "
        f"({len(result.matched)} of {result.required_count} required skills)",
        "",
    ]

    lines += _section("MATCHED", result.matched, "None of the required skills were found.")
    lines += _section("MISSING", result.missing, "Nothing missing - every required skill appears.")

    if result.extra:
        lines += _section("ALSO IN YOUR RESUME (not required)", result.extra, "")

    lines += ["ATS PARSEABILITY", "-" * 48]
    if issues:
        lines += [f"  [{issue.severity.upper()}] {issue.message}" for issue in issues]
    else:
        lines.append("  No structural issues detected.")
    lines.append("")

    return "\n".join(lines)


def _section(title: str, items: list[str], empty_message: str) -> list[str]:
    lines = [title, "-" * 48]
    lines += [f"  {item}" for item in items] if items else [f"  {empty_message}"]
    lines.append("")
    return lines


