from pathlib import Path
from uuid import uuid4

from flask import current_app

from database.db import db
from database.models import ATSResult, Candidate, JobRequirement
from nlp.ats_engine import calculate_ats
from nlp.extractor import extract_candidate
from nlp.ranking_engine import rank_and_shortlist
from nlp.text_cleaner import clean_text
from parsers.file_handler import allowed_file, delete_file, extract_text_by_type, safe_filename


def create_job_from_form(user_id, form):
    job = JobRequirement(
        user_id=user_id,
        role=(form.get("role") or "").strip(),
        required_skills=(form.get("required_skills") or "").strip(),
        experience_required=float(form.get("experience_required") or 0),
        openings=int(form.get("openings") or 0),
        job_description=(form.get("job_description") or "").strip(),
    )
    db.session.add(job)
    db.session.commit()
    return job


def process_resumes(user_id, form, files):
    job = create_job_from_form(user_id, form)
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    ats_results = []
    errors = []

    for file_storage in files:
        if not file_storage or not file_storage.filename:
            continue
        if not allowed_file(file_storage.filename):
            errors.append(f"{file_storage.filename}: unsupported file type.")
            continue

        filename = f"{uuid4().hex}_{safe_filename(file_storage.filename)}"
        temp_path = upload_dir / filename
        try:
            file_storage.save(temp_path)
            raw_text = extract_text_by_type(temp_path)
            text = clean_text(raw_text)
            if not text:
                errors.append(f"{file_storage.filename}: no readable resume text found.")
                continue

            extracted = extract_candidate(text)
            candidate = Candidate(
                user_id=user_id,
                job_id=job.id,
                name=extracted["name"],
                email=extracted["email"],
                phone=extracted["phone"],
                skills=", ".join(extracted["skills"]),
                experience=extracted["experience"],
                education=extracted["education"],
                links=", ".join(extracted["links"]),
                resume_summary=extracted["resume_summary"],
            )
            db.session.add(candidate)
            db.session.flush()

            scores = calculate_ats(job, extracted, text)
            ats = ATSResult(
                user_id=user_id,
                job_id=job.id,
                candidate_id=candidate.id,
                ats_score=scores["ats_score"],
                skills_score=scores["skills_score"],
                semantic_score=scores["semantic_score"],
                experience_score=scores["experience_score"],
                bonus_score=scores["bonus_score"],
                missing_skills=", ".join(scores["missing_skills"]),
                status=scores["status"],
            )
            db.session.add(ats)
            db.session.flush()
            ats_results.append(ats)
        except Exception as exc:
            current_app.logger.exception("Resume processing failed")
            errors.append(f"{file_storage.filename}: {exc}")
        finally:
            delete_file(temp_path)

    db.session.commit()
    rank_and_shortlist(user_id, job.id, ats_results, job.openings)
    return job, errors

