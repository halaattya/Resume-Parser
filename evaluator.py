import argparse
import time
from pathlib import Path

from .readers import get_reader
from .parser import ResumeParser
from .exporter import build_output, write_json

SUPPORTED = [".pdf", ".docx", ".txt", ".md"]


def process_file(path: Path, output_path: str) -> None:
    ext = path.suffix.lower()
    ReaderClass = get_reader(ext)

    if ReaderClass is None:
        print(f"Unsupported file type: {path.suffix}")
        return

    print(f"Parsing {path.name}...")

    t0 = time.time()
    try:
        reader = ReaderClass(str(path))
        lines = reader.extract_lines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not lines:
        print(f"No text found in {path.name}, skipping.")
        return

    parser = ResumeParser()
    resume = parser.parse(lines)
    elapsed = time.time() - t0

    output = build_output(resume, str(path), elapsed)
    write_json(output, output_path)

    score = output["evaluation"]["overall_score"]
    level = output["evaluation"]["completeness_level"]
    print(f"Done! Output: {output_path}  |  score: {score:.2f}/1.00 ({level})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Resume Parser")
    ap.add_argument("--input",  required=True, help="Path to resume file (.pdf, .docx, .txt, .md)")
    ap.add_argument("--output", default="output.json", help="Output JSON path")
    args = ap.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return

    process_file(input_path, args.output)


if __name__ == "__main__":
    main()
