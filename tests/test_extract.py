import io

import pytest
from pypdf import PdfWriter

from jd_match.extract import MAX_BYTES, ExtractionError, from_bytes


def _pdf_without_text() -> bytes:
    """Stands in for a scan: a valid PDF carrying no text layer."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _pdf_with_text(text: str) -> bytes:
    """Minimal single-page PDF that does carry a text layer."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R"
        b" /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    start = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        start,
    )
    return bytes(out)


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


def test_pdf_without_a_text_layer_is_rejected():
    with pytest.raises(ExtractionError, match="no readable text layer"):
        from_bytes(_pdf_without_text(), "resume.pdf")


def test_pdf_with_a_text_layer_is_extracted():
    body = "Python SQL and AWS experience building REST APIs for payment systems"
    assert "Python" in from_bytes(_pdf_with_text(body), "resume.pdf")


