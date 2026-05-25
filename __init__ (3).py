"""
DOCX resume reader using python-docx.
"""

from ..utils.text_utils import clean_text, split_lines


class DocxReader:
    """Extracts text lines from a .docx resume."""

    def __init__(self, path: str) -> None:
        self.path = path

    def extract_lines(self):
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx is required: pip install python-docx")

        doc = Document(self.path)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)
        return lines
