import pytest

from jd_match.extract import MAX_BYTES, ExtractionError, from_bytes


def test_plain_text_is_decoded():
    assert from_bytes(b"Python and SQL", "notes.txt") == "Python and SQL"


def test_unsupported_extension_is_rejected():
    with pytest.raises(ExtractionError, match="Unsupported file type"):
        from_bytes(b"data", "resume.rtf")


def test_oversized_file_is_rejected_before_parsing():
    with pytest.raises(ExtractionError, match="5 MB"):
        from_bytes(b"x" * (MAX_BYTES + 1), "resume.txt")


def test_corrupt_docx_raises_a_clean_error():
    with pytest.raises(ExtractionError, match="Could not read"):
        from_bytes(b"not really a docx", "resume.docx")


