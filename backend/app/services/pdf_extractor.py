"""
PDF text extraction service.

Strategy:
  1. Try pdfplumber (best for text-based PDFs).
  2. Fall back to PyPDF2 if pdfplumber fails or yields empty text.
  3. If both fail, return a structured failure result so the caller can
     surface a meaningful message to the user rather than an unhandled error.

We intentionally do NOT attempt OCR on scanned PDFs because that would
require Tesseract/image dependencies that may not be available.  The error
message directs users to provide a text-based PDF.
"""

import logging
import io
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    text: str = ""
    method: str = "none"
    success: bool = False
    page_count: int = 0
    warning: str = ""


def extract_text(file_bytes: bytes) -> ExtractionResult:
    """
    Extract text from PDF bytes.  Tries pdfplumber first, then PyPDF2.

    Args:
        file_bytes: Raw PDF file content as bytes.

    Returns:
        ExtractionResult with the extracted text and metadata.
    """
    result = _try_pdfplumber(file_bytes)
    if result.success and result.text.strip():
        return result

    logger.info("pdfplumber returned empty text; trying PyPDF2 fallback")
    fallback = _try_pypdf2(file_bytes)
    if fallback.success and fallback.text.strip():
        return fallback

    # Both methods returned empty or failed
    return ExtractionResult(
        text="",
        method="failed",
        success=False,
        warning=(
            "No text could be extracted from this PDF. "
            "The file may be scanned or image-only. "
            "Please upload a text-based PDF for accurate analysis."
        ),
    )


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def _try_pdfplumber(file_bytes: bytes) -> ExtractionResult:
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            text = "\n".join(pages)
            return ExtractionResult(
                text=text,
                method="pdfplumber",
                success=True,
                page_count=len(pdf.pages),
            )
    except ImportError:
        logger.warning("pdfplumber not installed; skipping")
        return ExtractionResult(success=False, method="pdfplumber_missing")
    except Exception as exc:
        logger.warning("pdfplumber extraction failed: %s", exc)
        return ExtractionResult(success=False, method="pdfplumber_error")


def _try_pypdf2(file_bytes: bytes) -> ExtractionResult:
    try:
        import PyPDF2  # type: ignore

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
        text = "\n".join(pages)
        return ExtractionResult(
            text=text,
            method="pypdf2",
            success=True,
            page_count=len(reader.pages),
        )
    except ImportError:
        logger.warning("PyPDF2 not installed; skipping")
        return ExtractionResult(success=False, method="pypdf2_missing")
    except Exception as exc:
        logger.warning("PyPDF2 extraction failed: %s", exc)
        return ExtractionResult(success=False, method="pypdf2_error")
