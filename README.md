# jd-match

Compare a resume against a job description: keyword coverage and ATS parsing risks.

**[Try it live](https://jd-match.streamlit.app/)** · no signup, nothing stored

![tests](https://github.com/Aswind-S-Varman/jd-match/actions/workflows/tests.yml/badge.svg)

## The problem

Most applications are filtered by keyword-matching software before a human reads them.
Two things get candidates screened out: the resume uses different words than the posting,
or its formatting can't be parsed at all. Neither failure produces any feedback.

`jd-match` reports both.

## What it does

- Extracts required skills from a job description and checks which appear in the resume
- Reports coverage, matched skills, missing skills, and skills you have that weren't asked for
- Flags DOCX formatting that commonly breaks parsers: tables, images, text boxes, columns,
  header/footer text, and fonts below 10pt
- Reads `.txt`, `.md`, `.docx`, and `.pdf`
- Runs offline, with no API key and no cost

## Quick start

```bash
pip install -e .
jd-match samples/sample_resume.md samples/sample_jd.txt
```

```
Coverage: 78% (7 of 9 required skills)

MATCHED
  aws, git, python, rest api, sql, agile, jira

MISSING
  docker, kubernetes

ATS PARSEABILITY
  No structural issues detected.
```

Web interface:

```bash
pip install -e ".[app]"
streamlit run app.py
```

## How it works

```
app.py / cli.py          interface layers - no logic
  └─ extract.py          bytes -> text (txt, md, docx, pdf)
  └─ keywords.py         text -> canonical skill names
       └─ skills.py      curated vocabulary with aliases
  └─ matcher.py          set comparison, coverage
  └─ ats_checks.py       DOCX structural inspection
  └─ report.py           plain-text rendering
```

## Design decisions

**Rules first, AI later.** Most of this problem is exact term matching, and rules solve it
for free, instantly, deterministically, and testably. An optional LLM pass for semantic
matches — recognising that "microservices communication" and "REST API integration"
describe the same experience — is a planned enhancement behind a flag, not a dependency.
The tool works with no network and no API key.

**A curated vocabulary, not statistical extraction.** Frequency analysis on a job posting
surfaces "team", "strong", and "fast-paced" alongside real skills. A controlled list of
skills and their aliases produces output that is explainable and testable. The cost is
maintenance: a skill the dictionary doesn't know is silently invisible. I hit this during
development when a test failed on a missing entry. A future improvement is logging
unmatched capitalised terms so gaps surface automatically instead of by accident.

**Whole-token matching.** Text is lowercased and padded with spaces so `" go "` matches
only the standalone word. A naive substring check matches "going", "Google", and
"algorithm" — silently, with no error, producing a confidently wrong answer.

**Nothing is stored.** Uploads are processed as bytes in memory and never written to disk.
Files are size-capped at 5 MB before parsing, because a small `.docx` is a ZIP archive that
can decompress to gigabytes. Parsing exceptions are caught and replaced with clean messages
so file contents never reach logs or tracebacks. Holding no personal data removes most of
the obligation that comes with handling it.

**ATS checks only run on DOCX.** These inspect document structure, which plain text doesn't
have and which PDF exposes unreliably. Returning nothing for unsupported formats is more
honest than pretending to check and always passing.

## Known limitations

- A scanned PDF with no text layer yields no text, and the tool reports 0% coverage rather
  than explaining why
- All required skills are weighted equally; "must have" and "nice to have" are not
  distinguished
- English only

## Tests

```bash
pip install -e ".[dev]"
pytest -v
```

Tests target the parts most likely to fail silently: substring false positives, alias
resolution, coverage arithmetic, and the upload size and corruption guards.

## License

MIT


