import re

from nlp.nlp_processor import process_text
from nlp.skill_matcher import detect_skills
from nlp.skills_db import ALL_SKILLS

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4}")
LINK_RE = re.compile(r"https?://[^\s]+|(?:linkedin\.com|github\.com)/[^\s]+", re.IGNORECASE)
EXP_RE = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)
EDU_RE = re.compile(r"\b(B\.?Tech|M\.?Tech|BSc|MSc|MBA|BCA|MCA|Bachelor|Master|PhD|Diploma)\b.*", re.IGNORECASE)

SECTION_HEADERS = {
    "skills", "technical skills", "projects", "project", "education", "experience",
    "work experience", "professional experience", "certifications", "certification",
    "summary", "profile", "objective", "career objective", "about me", "contact",
    "personal details", "achievements", "interests", "languages", "declaration",
    "internship", "internships", "training", "tools", "technologies",
}

ROLE_OR_RESUME_WORDS = {
    "resume", "cv", "curriculum", "vitae", "profile", "portfolio", "developer",
    "engineer", "designer", "analyst", "consultant", "manager", "student", "intern",
    "fresher", "professional", "specialist", "architect", "lead", "administrator",
}

PROJECT_WORDS = {
    "project", "system", "application", "app", "platform", "website", "portal",
    "dashboard", "management", "prediction", "detection", "classification", "analysis",
    "clone", "tracker", "automation", "chatbot", "model", "tool",
}

EDUCATION_WORDS = {
    "btech", "mtech", "b.sc", "m.sc", "bsc", "msc", "mba", "bca", "mca",
    "bachelor", "master", "phd", "diploma", "university", "college", "school",
    "institute", "degree", "cgpa", "gpa",
}

NAME_PREFIXES = {"mr", "mrs", "ms", "miss", "dr", "prof"}
TECH_KEYWORDS = {
    skill.lower() for skill in ALL_SKILLS if len(skill) > 1 and skill.lower() not in {"c"}
} | {
    "python", "java", "javascript", "typescript", "sql", "react", "html", "css",
    "machine learning", "data science", "firebase", "django", "flask", "node",
    "node.js", "mongodb", "mysql", "postgresql", "aws", "azure", "docker",
    "kubernetes", "tensorflow", "pytorch", "nlp", "ai", "ml", "power bi",
}

# Name extraction examples handled by the validator:
# 1. "Gurunath Patil" on the first line is accepted.
# 2. Email/phone lines before "Gurunath Patil" are ignored, then the name is accepted.
# 3. "Python | React | SQL" near the top is rejected as technical content.
# 4. "AI Resume Screening System" near the top is rejected as a project title.


def _normalize_line(line):
    line = re.sub("^[\\s\\-\\u2022*\\u25cf\\u25aa\\u25ab]+", "", line or "")
    line = re.sub(r"\s+", " ", line).strip()
    return line.strip(":-\u2013\u2014 ")


def _strip_name_prefixes(line):
    words = line.split()
    while words:
        first = words[0].rstrip(".").lower()
        if first not in NAME_PREFIXES:
            break
        words = words[1:]
    return " ".join(words)


def _contains_contact_or_link(line):
    lowered = line.lower()
    return bool(
        EMAIL_RE.search(line)
        or PHONE_RE.search(line)
        or LINK_RE.search(line)
        or "linkedin" in lowered
        or "github" in lowered
        or "http" in lowered
        or "www." in lowered
    )


def _is_section_header(line):
    lowered = re.sub(r"[^a-z ]", " ", line.lower())
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered in SECTION_HEADERS or (len(lowered.split()) <= 3 and any(header == lowered for header in SECTION_HEADERS))


def _contains_any_word(line, words):
    tokens = set(re.findall(r"[a-zA-Z.]+", line.lower()))
    compact = line.lower()
    return any(word in tokens or (" " in word and re.search(r"\b" + re.escape(word) + r"\b", compact)) for word in words)


def _technical_keyword_count(line):
    lowered = line.lower()
    tokens = set(re.findall(r"[a-zA-Z+#.]+", lowered))
    count = 0
    for keyword in TECH_KEYWORDS:
        if " " in keyword or "." in keyword or "+" in keyword or "#" in keyword:
            if re.search(r"\b" + re.escape(keyword) + r"\b", lowered):
                count += 1
        elif keyword in tokens:
            count += 1
    return count


def _format_name(line):
    formatted = []
    for word in line.split():
        clean = word.strip(".")
        if len(clean) == 1:
            formatted.append(clean.upper())
        else:
            formatted.append(clean[:1].upper() + clean[1:].lower())
    return " ".join(formatted)


def _looks_like_valid_name(line):
    line = _strip_name_prefixes(_normalize_line(line))
    if not line or len(line) > 60:
        return False, ""
    if _contains_contact_or_link(line) or _is_section_header(line):
        return False, ""
    blocked_symbols = [",", "|", "/", "\\", "\u2022", "*", "=", "<", ">", "[", "]", "{", "}", "(", ")"]
    if any(symbol in line for symbol in blocked_symbols):
        return False, ""
    if re.search(r"\d", line):
        return False, ""
    if _contains_any_word(line, EDUCATION_WORDS) or _contains_any_word(line, ROLE_OR_RESUME_WORDS):
        return False, ""
    if _contains_any_word(line, PROJECT_WORDS):
        return False, ""
    if _technical_keyword_count(line) >= 1:
        return False, ""

    words = line.split()
    if not 2 <= len(words) <= 4:
        return False, ""

    alpha_chars = sum(1 for char in line if char.isalpha())
    visible_chars = sum(1 for char in line if not char.isspace())
    if not visible_chars or alpha_chars / visible_chars < 0.82:
        return False, ""

    for word in words:
        clean = word.strip(". '-")
        if not clean.isalpha():
            return False, ""
        if len(clean) == 1 and not clean.isupper():
            return False, ""
        if len(clean) > 1 and clean.lower() in ROLE_OR_RESUME_WORDS:
            return False, ""

    return True, _format_name(line)


def extract_name(lines, entities):
    top_lines = [_normalize_line(line) for line in lines[:10] if _normalize_line(line)]
    for line in top_lines:
        is_valid, name = _looks_like_valid_name(line)
        if is_valid:
            return name

    top_text = "\n".join(top_lines).lower()
    for text, label in entities:
        if label != "PERSON":
            continue
        if text.lower() not in top_text:
            continue
        is_valid, name = _looks_like_valid_name(text)
        if is_valid:
            return name

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
