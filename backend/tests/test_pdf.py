import io
import pytest
from app.services.pdf_extractor import extract_text, ExtractionResult

def test_empty_bytes_returns_failure():
    result = extract_text(b"")
    assert result.success is False
    assert result.text == ""

def test_non_pdf_bytes_returns_failure():
    result = extract_text(b"this is not a pdf at all")
    assert result.success is False

def test_result_has_warning_on_failure():
    result = extract_text(b"garbage")
    assert result.warning != ""

def test_extraction_result_defaults():
    r = ExtractionResult()
    assert r.success is False
    assert r.text == ""
    assert r.page_count == 0
