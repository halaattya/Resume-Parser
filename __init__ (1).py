import re
from typing import List, Dict, Tuple, Optional

from .models.resume import ParsedResume, ContactInfo, EducationEntry, ExperienceEntry
from .utils.text_utils import extract_date_range
from .utils.section_detector import looks_like_heading, classify_heading

_EMAIL_RE    = re.compile(r"[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}")
_PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.I)
_GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.I)

_DATE_RANGE_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}|\d{4})"
    r"\s*[-–—]\s*"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{4}|\d{4}|[Pp]resent|[Cc]urrent|[Nn]ow)",
    re.I,
)

_BULLET_RE = re.compile(r"^[\-\*•▪▸◦‣>]+\s*")


def _strip_bullet(line: str) -> str:
    return _BULLET_RE.sub("", line).strip()


def _is_bullet(line: str) -> bool:
    return bool(_BULLET_RE.match(line))


def _split_into_sections(lines: List[str]) -> List[Tuple[Optional[str], List[str]]]:
    sections: List[Tuple[Optional[str], List[str]]] = []
    current_type: Optional[str] = None
    current_lines: List[str] = []

    for line in lines:
        if looks_like_heading(line):
            classified = classify_heading(line)
            if classified is not None:
                if current_lines:
                    sections.append((current_type, current_lines))
                current_type = classified
                current_lines = []
                continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_type, current_lines))

    return sections


def _extract_name(lines: List[str]) -> Optional[str]:
    # usually the first line, title case, 2-4 words, no digits
    for line in lines[:5]:
        stripped = line.strip()
        words = stripped.split()
        if (2 <= len(words) <= 5
                and all(re.match(r"^[A-Za-z\-']+$", w) for w in words)
                and stripped[0].isupper()):
            return stripped
    return None


def _extract_contact(lines: List[str]) -> ContactInfo:
    full_text = " ".join(lines)
    contact = ContactInfo()

    m = _EMAIL_RE.search(full_text)
    if m:
        contact.email = m.group(0)

    m = _PHONE_RE.search(full_text)
    if m:
        contact.phone = m.group(1).strip()

    m = _LINKEDIN_RE.search(full_text)
    if m:
        contact.linkedin = "https://" + m.group(0)

    m = _GITHUB_RE.search(full_text)
    if m:
        contact.github = "https://" + m.group(0)

    # TODO: improve location extraction, currently misses some formats
    loc_m = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Za-z]{2,})", full_text)
    if loc_m:
        contact.location = loc_m.group(1)

    return contact


def _extract_summary(lines: List[str]) -> str:
    return " ".join(lines).strip()


def _extract_skills(lines: List[str]) -> List[str]:
    skills: List[str] = []
    for line in lines:
        clean = re.sub(r"^[^:]+:\s*", "", _strip_bullet(line))
        parts = re.split(r"[,|;/]+", clean)
        for p in parts:
            p = p.strip().strip(".")
            if p and 1 < len(p) < 50:
                skills.append(p)
    return skills


def _extract_languages(lines: List[str]) -> List[str]:
    langs: List[str] = []
    for line in lines:
        clean = _strip_bullet(line)
        clean = re.sub(
            r"\b(native|fluent|advanced|intermediate|basic|beginner|"
            r"mother\s*tongue|c1|c2|b1|b2|a1|a2|professional|conversational)\b",
            "", clean, flags=re.I
        ).strip(" :-–()")
        parts = re.split(r"[,;/|]+", clean)
        for p in parts:
            p = p.strip()
            if p and 1 < len(p) < 40:
                langs.append(p)
    return langs


def _extract_education(lines: List[str]) -> List[EducationEntry]:
    entries: List[EducationEntry] = []
    current: Optional[EducationEntry] = None

    for line in lines:
        start, end = extract_date_range(line)

        if start and not _is_bullet(line):
            if current:
                entries.append(current)
            current = EducationEntry(institution=line, start_date=start, end_date=end)
            continue

        deg_m = re.search(
            r"\b(Bachelor|Master|B\.?Sc|M\.?Sc|B\.?A|M\.?A|PhD|Diploma|"
            r"Informatik|Computer Science|Engineering|Studium)\b",
            line, re.I
        )
        if deg_m:
            if current is None:
                current = EducationEntry(institution=line)
            else:
                if not current.degree:
                    current.degree = line
            continue

        gpa_m = re.search(r"(?:GPA|Grade|Average|Durchschnitt)[:\s]+([0-9.,]+)", line, re.I)
        if gpa_m and current:
            current.gpa = gpa_m.group(1)
            continue

        if not start and not _is_bullet(line) and re.match(r"[A-Z]", line):
            if current is None:
                current = EducationEntry(institution=line)
            elif not current.institution:
                current.institution = line

    if current:
        entries.append(current)

    return entries


def _extract_experience(lines: List[str]) -> List[ExperienceEntry]:
    entries: List[ExperienceEntry] = []
    current: Optional[ExperienceEntry] = None

    for line in lines:
        start, end = extract_date_range(line)

        if start and not _is_bullet(line):
            if current:
                entries.append(current)
            current = ExperienceEntry(company=line, start_date=start, end_date=end)
            continue

        if _is_bullet(line):
            if current is None:
                current = ExperienceEntry(company="")
            current.bullets.append(_strip_bullet(line))
            continue

        title_words = line.split()
        if (not start
                and 1 <= len(title_words) <= 8
                and re.match(r"[A-Z]", line)
                and not re.search(r"\d{4}", line)):
            if current is None:
                current = ExperienceEntry(company=line)
            elif not current.title:
                current.title = line
            elif not current.company or current.company == "":
                current.company = line

    if current:
        entries.append(current)

    return entries


def _extract_list_items(lines: List[str]) -> List[str]:
    items: List[str] = []
    for line in lines:
        clean = _strip_bullet(line).strip()
        if clean:
            items.append(clean)
    return items


class ResumeParser:

    def parse(self, lines: List[str]) -> ParsedResume:
        resume = ParsedResume()
        sections = _split_into_sections(lines)

        top_lines = [l for t, ls in sections[:2] if t in (None, "contact") for l in ls]
        if not top_lines:
            top_lines = lines[:10]

        resume.name = _extract_name(lines[:8])
        resume.contact = _extract_contact(top_lines + lines[:15])

        for section_type, sec_lines in sections:
            if not sec_lines:
                continue

            if section_type == "summary":
                resume.summary = _extract_summary(sec_lines)
            elif section_type == "education":
                resume.education = _extract_education(sec_lines)
            elif section_type == "experience":
                resume.experience = _extract_experience(sec_lines)
            elif section_type == "skills":
                resume.skills = _extract_skills(sec_lines)
            elif section_type == "languages":
                resume.languages = _extract_languages(sec_lines)
            elif section_type == "certifications":
                resume.certifications = _extract_list_items(sec_lines)
            elif section_type == "projects":
                resume.projects = _extract_list_items(sec_lines)

        return resume
