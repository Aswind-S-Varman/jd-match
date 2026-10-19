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
- Reads the posting's requirements section and names any term the vocabulary didn't
  recognise, so gaps in the coverage figure are visible rather than silent
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
RESUME vs JOB DESCRIPTION
================================================


Coverage: 50% (6 of 12 required skills)


REQUIREMENTS READ FROM THE JOB DESCRIPTION
------------------------------------------------
  Recognised 9 of 9 (100%)


MATCHED
------------------------------------------------
  agile
  aws
  docker
  python
  rest api
  sql


MISSING
------------------------------------------------
  ci/cd
  code review
  database design
  integration testing
  kubernetes
  microservices


ALSO IN YOUR RESUME (not required)
------------------------------------------------
  git
  javascript
  jira


ATS PARSEABILITY
------------------------------------------------
  No structural issues detected.
```


### Web interface


The hosted version at **[jd-match.streamlit.app](https://jd-match.streamlit.app/)** needs no
install. To run it locally instead:


```bash
pip install -e ".[app]"
streamlit run app.py
```


Then:


1. Open `http://localhost:8501` — Streamlit opens it for you on launch
2. Upload your resume under **Resume** (`.txt`, `.md`, `.docx`, or `.pdf`, up to 5 MB)
3. Paste the full job posting into **Job description**, headings and bullets included — the
   requirements section is found by its heading, so pasting only the bullet list skips that
   part of the analysis
4. Select **Compare**
5. Read the three headline figures, then open the tabs for detail:
   - **Skills** — missing and matched terms as chips
   - **Requirements** — every term read from the requirements section, and whether it could
     be checked
   - **ATS** — structural problems, DOCX only


Nothing is uploaded anywhere or written to disk. Files are parsed in memory and discarded
when the comparison finishes.


## Reading the results


The comparison sorts every skill term into one of three groups. They answer different
questions, and only one of them is a to-do list.


**Matched** — in both the posting and your resume. These are the terms a keyword filter will
find. Nothing to do; the group exists so you can confirm the important ones are actually
there, and spot it immediately when a rewrite drops one by accident.


**Missing** — in the posting but not your resume. This is the actionable group. For each
term, you either have the experience and described it in different words, in which case
adopt the posting's wording, or you genuinely don't have it, in which case you now know
what the gap is. The tool matches words, not ability — adding a keyword you can't speak to
in an interview trades a screening problem for a worse one.


**Also in your resume (not required)** — in your resume but not this posting. Not penalised,
and not a list to delete. It shows what this particular application is spending space on.
If your strongest material is buried under terms this employer never asked for, that's
worth knowing. Those same terms may be exactly right for the next posting.


### The two percentages


**Keyword coverage** is matched ÷ (matched + missing). One caveat worth understanding: it
counts skill terms found *anywhere* in the posting, including the responsibilities section.
In the sample above, `microservices`, `integration testing`, and `code review` come from
Responsibilities rather than Requirements, which is why coverage is measured against 12
terms while only 9 requirements were read. Treat it as a relevance signal, not a score.
Every term is weighted equally, and optional ones ("a plus", "nice to have") are labelled
but not discounted.


**Requirements read** is how much of the requirements section the vocabulary recognised. It
rates the tool, not you. At 100% every requirement was understood well enough to check
against your resume. Lower means some requirement used wording the vocabulary doesn't know,
so it was listed but never verified — and coverage should be read as approximate.


## How it works


```
app.py / cli.py          interface layers - no logic
  └─ extract.py          bytes -> text (txt, md, docx, pdf)
  └─ keywords.py         text -> canonical skill names
       └─ skills.py      curated vocabulary with aliases
  └─ matcher.py          set comparison, coverage
  └─ requirements.py     posting -> requirement terms, recognised or not
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


**Whole-token matching.** Text is lowercased, then skills are matched with a regex that
refuses to begin or end inside another token. A naive substring check matches "going",
"Google", and "algorithm" — silently, with no error, producing a confidently wrong answer.
The boundary also reasons about dots, so `node.js` stays whole while a trailing full stop in
`Python.` is not treated as part of the name. Aliases are tried longest-first, so `node.js`
wins over `node` and `javascript` over `java`.


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
- Optional requirements ("a plus", "nice to have") are detected and labelled, but coverage
  still weights every required skill equally
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








