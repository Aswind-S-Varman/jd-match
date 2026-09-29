from .ats_checks import Issue
from .matcher import MatchResult
from .requirements import Extraction


def render(result: MatchResult, issues: list[Issue], extraction: Extraction) -> str:
    lines = [
        "RESUME vs JOB DESCRIPTION",
        "=" * 48,
        "",
        f"Coverage: {result.coverage:.0%} "
        f"({len(result.matched)} of {result.required_count} required skills)",
        "",
    ]

    lines += _requirements_section(extraction)
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


def _requirements_section(extraction: Extraction) -> list[str]:
    lines = ["REQUIREMENTS READ FROM THE JOB DESCRIPTION", "-" * 48]

    if not extraction.section_found:
        lines += ["  No requirements section found, so this check was skipped.", ""]
        return lines
    if not extraction.requirements:
        lines += ["  A requirements section was found, but no skills could be read from it.", ""]
        return lines

    lines.append(
        f"  Recognised {len(extraction.recognised)} of {len(extraction.requirements)} "
        f"({extraction.recognition:.0%})"
    )

    if extraction.unrecognised:
        lines += ["", "  Not in the skill vocabulary, so not checked against your resume:"]
        lines += [
            f"    {r.text}{' (optional)' if r.optional else ''}" for r in extraction.unrecognised
        ]

    lines.append("")
    return lines


