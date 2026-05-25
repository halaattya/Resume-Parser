# Resume Parser


A Python tool that takes a resume (PDF, DOCX, or TXT) and extracts structured data from it — name, contact info, education, experience, skills, languages, projects — and outputs everything as JSON.


Built as a personal project after working on document processing during my internship. No external NLP APIs, everything runs locally.

## What it does

- Reads PDF, DOCX, TXT, and Markdown resumes
- Detects section headings and classifies them (education, experience, skills, etc.)
- Extracts contact fields using regex (email, phone, LinkedIn, GitHub)
- Parses education entries with institution, degree, dates, GPA
- Parses experience entries with company, title, date range, and bullet points
- Scores each field with a confidence value (0.0–1.0) and gives an overall completeness score

## Project structure


```
resume_parser/
├── main.py
├── parser.py            # main logic — section splitting + field extraction
├── evaluator.py         # confidence scoring
├── exporter.py          # builds and writes the JSON output
├── readers/
│   ├── pdf_reader.py
│   ├── docx_reader.py
│   └── txt_reader.py
├── models/
│   └── resume.py        # dataclasses for the output structure
└── utils/
    ├── text_utils.py    # cleaning, date parsing
    └── section_detector.py  # heading detection + classification
```

## Setup

```bash
git clone https://github.com/<your-username>/resume-parser.git
cd resume-parser
pip install -r requirements.txt
```

## Usage

```bash
python -m resume_parser.main --input resume.pdf --output result.json
```

## Example output

```json
{
  "document_metadata": {
    "filename": "resume.pdf",
    "file_type": "pdf",
    "processing_date": "2026-05-25T16:00:00Z",
    "processing_time_seconds": 0.04
  },
  "parsed_resume": {
    "name": "Hala Atiyeh",
    "contact": {
      "email": "hala@email.com",
      "phone": "+49 123 456789",
      "linkedin": "https://linkedin.com/in/hala-atiyeh",
      "github": "https://github.com/hala-atiyeh",
      "location": "Gießen, Germany"
    },
    "education": [
      {
        "institution": "German Jordanian University",
        "degree": "B.Sc. Computer Science",
        "start_date": "Sep 2021",
        "end_date": "Jun 2025",
        "gpa": "3.7"
      }
    ],
    "experience": [
      {
        "company": "Insightix",
        "title": "AI & Data Science Intern",
        "start_date": "Jun 2024",
        "end_date": "Sep 2024",
        "bullets": [
          "Developed a document chunking system using NLP and TF-IDF",
          "Built topic-based segmentation for PDF, DOCX, and TXT files"
        ]
      }
    ],
    "skills": ["Python", "Flutter", "Firebase", "NLP", "SQL"],
    "languages": ["Arabic", "English", "German"],
    "projects": ["AutiCare - Flutter/Firebase app for children with autism"]
  },
  "evaluation": {
    "field_scores": {
      "name": 1.0, "email": 1.0, "phone": 1.0,
      "skills": 1.0, "experience": 1.0, "education": 1.0
    },
    "overall_score": 0.917,
    "completeness_level": "high",
    "missing_fields": ["certifications"]
  }
}
```

## Evaluation


Each field gets a score from 0.0 to 1.0. Boolean fields (name, email, etc.) are 1.0 if found, 0.0 if not. List fields (skills, experience) are scored relative to an expected minimum. Experience and education get a small bonus if bullet points or degree info were detected.

The overall score is the average across all fields. Completeness levels: high (≥0.7), medium (≥0.4), low (<0.4).

## Known limitations


- Works best with clearly structured resumes
- Location extraction sometimes picks up wrong text (known issue, TODO)
- Scanned PDFs won't work since there's no OCR
- Company/title ordering in experience can get mixed up depending on resume format
