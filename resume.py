"""
PDF resume reader using pypdf.
"""

from ..utils.text_utils import clean_text, split_lines


class PdfReader:
    """Extracts text lines from a PDF resume."""

    def __init__(self, path: str) -> None:
        self.path = path

    def extract_lines(self):
        try:
            from pypdf import PdfReader as _PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF support: pip install pypdf")

        reader = _PdfReader(self.path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text)
        return split_lines(clean_text(full_text))
