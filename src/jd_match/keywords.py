import re

from .skills import ALIAS_TO_SKILL

_SPACES = re.compile(r"\s+")

# Characters that continue a skill token, so "java" cannot match inside "javascript".
_TOKEN = r"[a-z0-9+#]"

# Longest alias first, so "node.js" wins over "node" and "javascript" over "java".
_ALTERNATION = "|".join(
    re.escape(alias) for alias in sorted(ALIAS_TO_SKILL, key=len, reverse=True)
)

# A dot binds only when it joins two characters: "node.js" stays whole, "Python." does not.
_SKILL_RE = re.compile(
    rf"(?<!{_TOKEN})(?<![a-z0-9]\.)"
    rf"(?:{_ALTERNATION})"
    rf"(?!{_TOKEN})(?!\.[a-z0-9])"
)


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace. Punctuation is kept for boundary decisions."""
    return _SPACES.sub(" ", text.lower()).strip()


def find_skills(text: str) -> set[str]:
    """Canonical skill names present in the text."""
    return {ALIAS_TO_SKILL[m.group()] for m in _SKILL_RE.finditer(normalize(text))}


