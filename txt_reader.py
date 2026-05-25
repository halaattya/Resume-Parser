import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .models.resume import ParsedResume
from .evaluator import evaluate


def build_output(resume: ParsedResume, source_path: str, processing_time: float) -> Dict[str, Any]:
    eval_result = evaluate(resume)

    return {
        "document_metadata": {
            "filename": Path(source_path).name,
            "file_type": Path(source_path).suffix.lstrip("."),
            "processing_date": datetime.now(timezone.utc).isoformat(),
            "processing_time_seconds": round(processing_time, 3),
        },
        "parsed_resume": resume.to_dict(),
        "evaluation": eval_result,
    }


def write_json(data: Dict[str, Any], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
