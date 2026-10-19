import streamlit as st


from jd_match import ats_checks, matcher, requirements
from jd_match.extract import ExtractionError, from_bytes


st.set_page_config(page_title="jd-match", page_icon="📄", layout="centered")




@st.cache_data(show_spinner="Reading your resume and the posting\u2026")
def analyse(data: bytes, filename: str, job_text: str):
    """Cached so reruns and tab switches do not re-parse the upload."""
    resume_text = from_bytes(data, filename)
    return (
        matcher.compare(resume_text, job_text),
        ats_checks.check(data, filename),
        requirements.extract(job_text),
    )




def badges(items: list[str], color: str, icon: str = "") -> None:
    """Canonical skill names only. Uploaded text goes in a dataframe, not badge syntax."""
    if not items:
        st.caption("None")
        return
    prefix = f"{icon} " if icon else ""
    st.markdown(" ".join(f":{color}-badge[{prefix}{item}]" for item in sorted(items)))




st.title("jd-match")
st.markdown(
    ":gray[Compare a resume against a job description. "
    "Files are processed in memory and never stored.]"
)


with st.form("compare"):
    upload_col, paste_col = st.columns([1, 1.3], gap="large")
    with upload_col:
        uploaded = st.file_uploader("Resume", type=["txt", "md", "docx", "pdf"])
    with paste_col:
        job_text = st.text_area(
            "Job description", height=150, placeholder="Paste the job posting here"
        )
    submitted = st.form_submit_button(
        "Compare",
        type="primary",
        icon=":material/compare_arrows:",
        width="stretch",
    )


if submitted:
    st.session_state.pop("outcome", None)
    st.session_state.pop("problem", None)
    if uploaded is None or not job_text.strip():
        st.session_state["problem"] = (
            "warning",
            "Upload a resume and paste a job description first.",
        )
    else:
        try:
            st.session_state["outcome"] = analyse(
                uploaded.getvalue(), uploaded.name, job_text
            )
        except ExtractionError as exc:
            st.session_state["problem"] = ("error", str(exc))


problem = st.session_state.get("problem")
if problem:
    kind, message = problem
    if kind == "warning":
        st.warning(message, icon=":material/warning:")
    else:
        st.error(message, icon=":material/report:")


outcome = st.session_state.get("outcome")
if not outcome:
    if not problem:
        st.info(
            "Upload a resume and paste a job description, then select Compare.",
            icon=":material/arrow_upward:",
        )
    st.stop()


result, issues, extraction = outcome
severity = "none"
if issues:
    severity = "high" if any(i.severity == "high" for i in issues) else "medium"


coverage_col, ats_col = st.columns(2, gap="medium")


with coverage_col:
    with st.container(border=True, height="stretch"):
        st.metric("Keyword coverage", f"{result.coverage:.0%}", icon=":material/checklist:")
        st.progress(result.coverage)
        st.caption(f"{len(result.matched)} of {result.required_count} required skills")


with ats_col:
    with st.container(border=True, height="stretch"):
        st.metric(
            "ATS parseability",
            "Clear" if not issues else f"{len(issues)} issues",
            icon=":material/description:",
        )
        if not issues:
            st.markdown(":green-badge[:material/check_circle: No issues]")
        else:
            st.markdown(
                f":{'red' if severity == 'high' else 'orange'}-badge"
                f"[:material/warning: {severity.capitalize()} severity]"
            )


skills_tab, requirements_tab, ats_tab = st.tabs(
    [
        f"Skills ({len(result.matched)}/{result.required_count})",
        "Requirements"
        + (
            f" ({len(extraction.unrecognised)} unverified)"
            if extraction.unrecognised
            else ""
        ),
        "ATS" + (f" ({len(issues)})" if issues else ""),
    ]
)


with skills_tab:
    missing_col, matched_col = st.columns(2, gap="large")
    with missing_col:
        with st.container(border=True):
            st.markdown(f"#### Missing ({len(result.missing)})")
            badges(result.missing, "red", ":material/close:")
    with matched_col:
        with st.container(border=True):
            st.markdown(f"#### Matched ({len(result.matched)})")
            badges(result.matched, "green", ":material/check:")


    if result.extra:
        with st.expander(f"Also in your resume, not required ({len(result.extra)})"):
            badges(result.extra, "gray")


with requirements_tab:
    if not extraction.section_found:
        st.info(
            "No requirements section found in this posting, so this check was skipped. "
            "Keyword coverage was measured against the whole posting.",
            icon=":material/info:",
        )
    elif not extraction.requirements:
        st.info(
            "A requirements section was found, but no skills could be read from it.",
            icon=":material/info:",
        )
    else:
        st.metric(
            "Requirements read",
            f"{extraction.recognition:.0%}",
            icon=":material/manage_search:",
        )
        st.caption(
            f"{len(extraction.recognised)} of {len(extraction.requirements)} "
            "requirements recognised by the skill vocabulary"
        )


        if extraction.unrecognised:
            st.warning(
                "Some requirements are not in the skill vocabulary, so they were not "
                "checked against your resume. Treat the coverage figure as approximate.",
                icon=":material/warning:",
            )
        else:
            st.success(
                "Every requirement in this posting was recognised.",
                icon=":material/check_circle:",
            )


        st.dataframe(
            [
                {
                    "Term": r.text,
                    "Verified": "Yes" if r.recognised else "No",
                    "Optional": "Yes" if r.optional else "No",
                }
                for r in sorted(
                    extraction.requirements, key=lambda r: (r.recognised, r.text.lower())
                )
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "Term": st.column_config.TextColumn(width="large"),
                "Verified": st.column_config.TextColumn(
                    width="small",
                    help="Recognised by the skill vocabulary, so it could be checked "
                    "against your resume",
                ),
                "Optional": st.column_config.TextColumn(
                    width="small",
                    help="Listed as a plus or nice to have, not mandatory",
                ),
            },
        )


with ats_tab:
    if not issues:
        st.success("No structural issues detected.", icon=":material/check_circle:")
    else:
        for issue in issues:
            if issue.severity == "high":
                st.error(issue.message, icon=":material/report:")
            else:
                st.warning(issue.message, icon=":material/warning:")








