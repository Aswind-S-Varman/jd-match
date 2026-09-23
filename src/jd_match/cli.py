import argparse
from pathlib import Path

from . import ats_checks, matcher, report
from .extract import ExtractionError, from_path


def parse_args():
    parser = argparse.ArgumentParser(
        prog="jd-match",
        description="Compare a resume against a job description.",
    )
    parser.add_argument("resume", help="Resume file (.txt, .md, .docx, .pdf)")
    parser.add_argument("job_description", help="Job description file (.txt, .md, .docx, .pdf)")
    parser.add_argument("-o", "--output", help="Write the report to this file instead of stdout")
    return parser.parse_args()


def main():
    args = parse_args()
    resume_path = Path(args.resume)

    try:
        resume_text = from_path(resume_path)
        job_text = from_path(Path(args.job_description))
    except ExtractionError as exc:
        raise SystemExit(str(exc))

    result = matcher.compare(resume_text, job_text)
    issues = ats_checks.check(resume_path.read_bytes(), resume_path.name)
    output = report.render(result, issues)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()


