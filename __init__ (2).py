"""
Reader factory — returns the right reader class for a file extension.
"""

from .pdf_reader import PdfReader
from .docx_reader import DocxReader
from .txt_reader import TxtReader

_REGISTRY = {
    ".pdf":  PdfReader,
    ".docx": DocxReader,
    ".txt":  TxtReader,
    ".md":   TxtReader,
}


def get_reader(extension: str):
    """Return the reader class for the given file extension, or None."""
    return _REGISTRY.get(extension.lower())
