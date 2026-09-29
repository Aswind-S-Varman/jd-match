"""Requirements read from the job description itself, so unknown terms stay visible.

The skill vocabulary is used here to recognise terms, never to decide which terms count.
"""

import re
from dataclasses import dataclass

from .keywords import find_skills

_SECTION_START = re.compile(
    r"^\s*(requirements|qualifications|skills|what you.?ll need|"
    r"must have|about you|you have|tech stack)\b",
    re.I,
)
_SECTION_END = re.compile(
    r"^\s*(responsibilities|what you.?ll do|the role|benefits|"
    r"about us|what we offer|perks|how to apply)\b",
    re.I,
)
_BULLET = re.compile(r"^\s*[-*\u2022\u25cf]\s+|^\s*\d+[.)]\s+")
_OPTIONAL = re.compile(
    r"\b(a plus|nice to have|nice-to-have|preferred|bonus|desirable|advantageous)\b", re.I
)
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9+#./-]*")

# Prose that survives the capitalisation filter because it sits mid-line or reads as an acronym.
_STOP = frozenset(
    {
        "experience", "years", "year", "team", "teams", "role", "company", "candidate",
        "position", "job", "work", "english", "degree", "bs", "ba", "ms", "msc", "bsc",
        "phd", "mba", "us", "usa", "uk", "eu", "emea", "apac", "ideally", "minimum",
    }
)


@dataclass(frozen=True)
class Requirement:
    text: str
    skill: str | None
    optional: bool

    @property
    def recognised(self) -> bool:
        return self.skill is not None


@dataclass(frozen=True)
class Extraction:
    requirements: tuple[Requirement, ...]
    section_found: bool

    @property
    def recognised(self) -> list[Requirement]:
        return [r for r in self.requirements if r.recognised]

    @property
    def unrecognised(self) -> list[Requirement]:
        return sorted(
            (r for r in self.requirements if not r.recognised), key=lambda r: r.text.lower()
        )

    @property
    def recognition(self) -> float:
        if not self.requirements:
            return 0.0
        return len(self.recognised) / len(self.requirements)


def extract(job_text: str) -> Extraction:
    lines = _requirement_lines(job_text)
    if lines is None:
        return Extraction((), section_found=False)

    found: dict[str, Requirement] = {}
    for line, optional in lines:
        for text, skill in _candidates(line):
            key = skill or text.lower()
            seen = found.get(key)
            # A term demanded outright outranks the same term listed as a bonus.
            if seen is None or (seen.optional and not optional):
                found[key] = Requirement(text=text, skill=skill, optional=optional)

    return Extraction(tuple(found.values()), section_found=True)


def _requirement_lines(text: str) -> list[tuple[str, bool]] | None:
    """Bullets under a requirements heading, or None when no such heading exists."""
    lines: list[tuple[str, bool]] = []
    active = seen_heading = False

    for raw in text.splitlines():
        if _SECTION_START.search(raw):
            active = seen_heading = True
            continue
        if _SECTION_END.search(raw):
            active = False
            continue
        if active and _BULLET.search(raw):
            line = _BULLET.sub("", raw).strip()
            if line:
                lines.append((line, bool(_OPTIONAL.search(line))))

    return lines if seen_heading else None


def _candidates(line: str) -> list[tuple[str, str | None]]:
    tokens = [t.strip("./-") for t in _TOKEN.findall(line)]
    consumed = [False] * len(tokens)
    out: list[tuple[str, str | None]] = []

    # Vocabulary first, consuming what it claims, so "REST APIs" cannot also yield "REST".
    i = 0
    while i < len(tokens):
        pair = " ".join(tokens[i : i + 2])
        if i + 1 < len(tokens) and (hits := find_skills(pair)):
            out += [(pair, skill) for skill in sorted(hits)]
            consumed[i] = consumed[i + 1] = True
            i += 2
            continue
        if hits := find_skills(tokens[i]):
            out += [(tokens[i], skill) for skill in sorted(hits)]
            consumed[i] = True
        i += 1

    # Then harvest survivors that still look like product names.
    i = 0
    while i < len(tokens):
        if consumed[i] or not _has_signal(tokens[i], first=i == 0):
            i += 1
            continue
        term = tokens[i]
        if (
            i + 1 < len(tokens)
            and not consumed[i + 1]
            and _has_signal(tokens[i + 1], first=False)
            and term[:1].isupper()
            and tokens[i + 1][:1].isupper()
        ):
            term = f"{term} {tokens[i + 1]}"
            i += 1
        out.append((term, None))
        i += 1

    return out


def _has_signal(token: str, first: bool) -> bool:
    if len(token) < 2 or not any(c.isalpha() for c in token) or token.lower() in _STOP:
        return False

    acronym = token.isupper() and len(token) <= 6
    symbolic = any(c in token for c in "+#./")
    titled = token[:1].isupper() and not token.isupper()

    # Bullets open with a capital, so a plain capitalised first word is prose, not a skill.
    if first and titled and not symbolic:
        return False

    return acronym or symbolic or titled


