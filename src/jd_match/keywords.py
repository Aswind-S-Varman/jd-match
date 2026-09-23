import re

from .skills import SKILLS

# Keep characters that are part of real skill names: c++, ci/cd, node.js, c#
_KEEP = re.compile(r"[^a-z0-9+#./\- ]")
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Lowercase and pad with spaces so whole-token matching works."""
    text = _KEEP.sub(" ", text.lower())
    text = _SPACES.sub(" ", text).strip()
    return f" {text} "


def find_skills(text: str) -> set[str]:
    """Canonical skill names present in the text."""
    haystack = normalize(text)
    found = set()

    for canonical, aliases in SKILLS.items():
        if any(f" {alias} " in haystack for alias in aliases):
            found.add(canonical)

    return found


