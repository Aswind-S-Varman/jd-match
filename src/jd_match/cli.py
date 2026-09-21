import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        prog="jd-match",
        description="Compare a resume against a job description.",
    )
    parser.add_argument("resume", help="Path to the resume file")
    parser.add_argument("job_description", help="Path to the job description file")
    return parser.parse_args()


def main():
    args = parse_args()
    resume = Path(args.resume)
    job = Path(args.job_description)

    for path in (resume, job):
        if not path.exists():
            raise SystemExit(f"File not found: {path}")

    print(f"Resume: {resume.name} ({len(resume.read_text(encoding='utf-8'))} chars)")
    print(f"Job description: {job.name} ({len(job.read_text(encoding='utf-8'))} chars)")


if __name__ == "__main__":
    main()


