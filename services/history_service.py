from sqlalchemy import func

from database.models import ATSResult, Candidate, JobRequirement, ShortlistedCandidate


def user_jobs(user_id):
    return JobRequirement.query.filter_by(user_id=user_id).order_by(JobRequirement.created_at.desc()).all()


def get_owned_job(user_id, job_id):
    return JobRequirement.query.filter_by(user_id=user_id, id=job_id).first_or_404()


def job_stats(user_id, job_id):
    total_candidates = Candidate.query.filter_by(user_id=user_id, job_id=job_id).count()
    shortlisted = ShortlistedCandidate.query.filter_by(user_id=user_id, job_id=job_id).count()
    highest = (
        ATSResult.query.with_entities(func.max(ATSResult.ats_score))
        .filter_by(user_id=user_id, job_id=job_id)
        .scalar()
        or 0
    )
    average = (
        ATSResult.query.with_entities(func.avg(ATSResult.ats_score))
        .filter_by(user_id=user_id, job_id=job_id)
        .scalar()
        or 0
    )
    return {
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "highest": round(highest, 2),
        "average": round(average, 2),
    }


def results_for_job(user_id, job_id):
    job = get_owned_job(user_id, job_id)
    rows = (
        ATSResult.query.filter_by(user_id=user_id, job_id=job_id)
        .join(Candidate)
        .order_by(ATSResult.ats_score.desc())
        .all()
    )
    shortlisted = (
        ShortlistedCandidate.query.filter_by(user_id=user_id, job_id=job_id)
        .order_by(ShortlistedCandidate.rank.asc())
        .all()
    )
    return job, rows, shortlisted, job_stats(user_id, job_id)

