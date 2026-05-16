from config.constants import ATS_THRESHOLDS
from nlp.embedding_engine import semantic_similarity
from nlp.skill_matcher import required_skill_report
from nlp.skills_db import BONUS_SKILLS


def status_for_score(score):
    if score >= ATS_THRESHOLDS["excellent"]:
        return "Excellent Match"
    if score >= ATS_THRESHOLDS["good"]:
        return "Good Match"
    if score >= ATS_THRESHOLDS["moderate"]:
        return "Moderate Match"
    return "Weak Match"


def calculate_ats(job, candidate, resume_text):
    required, matched, missing = required_skill_report(job.required_skills, candidate.get("skills", []))
    skills_ratio = len(matched) / len(required) if required else 0
    skills_score = skills_ratio * 40

    job_text = f"{job.role} {job.required_skills} {job.experience_required} years {job.job_description}"
    candidate_text = " ".join(candidate.get("skills", [])) + f" {candidate.get('experience', 0)} years " + (resume_text or "")
    semantic = max(0.0, min(1.0, semantic_similarity(job_text, candidate_text)))
    semantic_score = semantic * 30

    required_exp = float(job.experience_required or 0)
    candidate_exp = float(candidate.get("experience") or 0)
    if required_exp <= 0:
        experience_score = 20
    elif candidate_exp >= required_exp:
        experience_score = 20
    elif candidate_exp > 0:
        experience_score = min(20, (candidate_exp / required_exp) * 20)
    else:
        experience_score = 5

    detected_bonus = set(candidate.get("skills", [])) & BONUS_SKILLS
    bonus_score = min(10, len(detected_bonus) * 2.5)

    total = min(100, max(0, skills_score + semantic_score + experience_score + bonus_score))
    return {
        "ats_score": round(total, 2),
        "skills_score": round(skills_score, 2),
        "semantic_score": round(semantic_score, 2),
        "experience_score": round(experience_score, 2),
        "bonus_score": round(bonus_score, 2),
        "missing_skills": missing,
        "status": status_for_score(total),
    }

