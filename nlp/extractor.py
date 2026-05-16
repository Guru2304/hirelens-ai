import re

from nlp.nlp_processor import process_text
from nlp.skill_matcher import detect_skills

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4}")
LINK_RE = re.compile(r"https?://[^\s]+|(?:linkedin\.com|github\.com)/[^\s]+", re.IGNORECASE)
EXP_RE = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)
EDU_RE = re.compile(r"\b(B\.?Tech|M\.?Tech|BSc|MSc|MBA|BCA|MCA|Bachelor|Master|PhD|Diploma)\b.*", re.IGNORECASE)


def extract_name(lines, entities):
    for text, label in entities:
        if label == "PERSON" and 2 <= len(text.split()) <= 4:
            return text.strip()
    for line in lines[:8]:
        clean = re.sub(r"[^A-Za-z .]", "", line).strip()
        if clean and 2 <= len(clean.split()) <= 4 and not EMAIL_RE.search(line):
            return clean
    return "Unknown Candidate"


def extract_experience(text):
    values = [float(match.group(1)) for match in EXP_RE.finditer(text or "")]
    return max(values) if values else 0.0


def extract_education(text):
    matches = [match.group(0).strip() for match in EDU_RE.finditer(text or "")]
    return ", ".join(dict.fromkeys(matches[:5]))


def extract_candidate(text):
    doc, sentences, entities = process_text(text)
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    skills = detect_skills(text, sentences)
    emails = EMAIL_RE.findall(text or "")
    phones = PHONE_RE.findall(text or "")
    links = LINK_RE.findall(text or "")

    return {
        "name": extract_name(lines, entities),
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "skills": skills,
        "experience": extract_experience(text),
        "education": extract_education(text),
        "links": sorted(set(links)),
        "resume_summary": "\n".join(sentences[:8])[:2000],
    }

