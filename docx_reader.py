"""
Plain text / Markdown resume reader.
"""

from ..utils.text_utils import clean_text, split_lines


class TxtReader:
    """Reads a .txt or .md file and returns lines."""

    def __init__(self, path: str) -> None:
        self.path = path

    def extract_lines(self):
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        return split_lines(clean_text(raw))
