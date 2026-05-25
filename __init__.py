from typing import Dict, Any
from .models.resume import ParsedResume


def _bool_score(value) -> float:
    return 1.0 if value else 0.0


def _list_score(lst, expected_min: int = 1) -> float:
    if not lst:
        return 0.0
    return min(1.0, len(lst) / expected_min)


def evaluate(resume: ParsedResume) -> Dict[str, Any]:
    scores: Dict[str, float] = {}

    scores["name"]     = _bool_score(resume.name)
    scores["email"]    = _bool_score(resume.contact.email)
    scores["phone"]    = _bool_score(resume.contact.phone)
    scores["linkedin"] = _bool_score(resume.contact.linkedin)
    scores["location"] = _bool_score(resume.contact.location)
    scores["summary"]        = _bool_score(resume.summary)
    scores["education"]      = _list_score(resume.education, expected_min=1)
    scores["experience"]     = _list_score(resume.experience, expected_min=1)
    scores["skills"]         = _list_score(resume.skills, expected_min=3)
    scores["languages"]      = _list_score(resume.languages, expected_min=1)
    scores["certifications"] = _list_score(resume.certifications, expected_min=1)
    scores["projects"]       = _list_score(resume.projects, expected_min=1)

    # bonus points if we found actual degree info or bullet points
    if resume.education and any(e.degree for e in resume.education):
        scores["education"] = min(1.0, scores["education"] + 0.2)
    if resume.experience and any(e.bullets for e in resume.experience):
        scores["experience"] = min(1.0, scores["experience"] + 0.2)

    overall = sum(scores.values()) / len(scores)
    missing = [k for k, v in scores.items() if v == 0.0]

    if overall >= 0.7:
        level = "high"
    elif overall >= 0.4:
        level = "medium"
    else:
        level = "low"

    return {
        "field_scores":       scores,
        "overall_score":      round(overall, 3),
        "completeness_level": level,
        "missing_fields":     missing,
    }
