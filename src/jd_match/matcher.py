from dataclasses import dataclass

from .keywords import find_skills


@dataclass
class MatchResult:
    matched: list[str]
    missing: list[str]
    extra: list[str]

    @property
    def required_count(self) -> int:
        return len(self.matched) + len(self.missing)

    @property
    def coverage(self) -> float:
        if self.required_count == 0:
            return 0.0
        return len(self.matched) / self.required_count


def compare(resume_text: str, job_text: str) -> MatchResult:
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_text)

    return MatchResult(
        matched=sorted(job_skills & resume_skills),
        missing=sorted(job_skills - resume_skills),
        extra=sorted(resume_skills - job_skills),
    )


