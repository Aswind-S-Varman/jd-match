import streamlit as st

from jd_match import ats_checks, matcher
from jd_match.extract import ExtractionError, from_bytes

st.set_page_config(page_title="jd-match", page_icon="📄")

st.title("jd-match")
st.caption(
    "Compare a resume against a job description. "
    "Files are processed in memory and never stored."
)

uploaded = st.file_uploader("Resume", type=["txt", "md", "docx", "pdf"])
job_text = st.text_area(
    "Job description",
    height=240,
    placeholder="Paste the job posting here",
)

if st.button("Compare", type="primary"):
    if uploaded is None or not job_text.strip():
        st.warning("Upload a resume and paste a job description first.")
        st.stop()

    data = uploaded.getvalue()

    try:
        resume_text = from_bytes(data, uploaded.name)
    except ExtractionError as exc:
        st.error(str(exc))
        st.stop()

    result = matcher.compare(resume_text, job_text)
    issues = ats_checks.check(data, uploaded.name)

    st.divider()
    st.metric(
        "Keyword coverage",
        f"{result.coverage:.0%}",
        help=f"{len(result.matched)} of {result.required_count} required skills found",
    )
    st.progress(result.coverage)

    left, right = st.columns(2)
    with left:
        st.subheader(f"Matched ({len(result.matched)})")
        st.markdown("\n".join(f"- {s}" for s in result.matched) or "_None_")
    with right:
        st.subheader(f"Missing ({len(result.missing)})")
        st.markdown("\n".join(f"- {s}" for s in result.missing) or "_None_")

    if result.extra:
        with st.expander(f"Also in your resume, not required ({len(result.extra)})"):
            st.markdown("\n".join(f"- {s}" for s in result.extra))

    st.subheader("ATS parseability")
    if issues:
        for issue in issues:
            show = st.error if issue.severity == "high" else st.warning
            show(issue.message)
    else:
        st.success("No structural issues detected.")


