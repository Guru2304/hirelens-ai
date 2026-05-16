import re

from config.constants import SKILL_MATCHING_THRESHOLD
from nlp.embedding_engine import calculate_text_similarity
from nlp.skills_db import ALL_SKILLS


def normalize_skill(skill):
    return re.sub(r"\s+", " ", (skill or "").strip()).lower()


def parse_required_skills(required_skills):
    pieces = re.split(r"[,;\n|]+", required_skills or "")
    return [piece.strip() for piece in pieces if piece.strip()]


def exact_skill_matches(text):
    found = []
    haystack = f" {text.lower()} "
    for skill in ALL_SKILLS:
        pattern = r"(?<![A-Za-z0-9+#.])" + re.escape(skill.lower()) + r"(?![A-Za-z0-9+#.])"
        if re.search(pattern, haystack):
            found.append(skill)
    return sorted(set(found))


def semantic_skill_matches(sentences):
    if not sentences:
        return []
    resume_context = " ".join(sentences[:80])
    try:
        return [
            skill
            for skill in ALL_SKILLS
            if calculate_text_similarity(skill, resume_context) >= SKILL_MATCHING_THRESHOLD
        ]
    except Exception:
        return []


def detect_skills(text, sentences=None):
    exact = exact_skill_matches(text)
    semantic = semantic_skill_matches(sentences or [])
    return sorted(set(exact + semantic))


def required_skill_report(required_skills, detected_skills):
    required = parse_required_skills(required_skills)
    detected_norm = {normalize_skill(skill) for skill in detected_skills}
    matched = [skill for skill in required if normalize_skill(skill) in detected_norm]
    missing = [skill for skill in required if normalize_skill(skill) not in detected_norm]
    return required, matched, missing


