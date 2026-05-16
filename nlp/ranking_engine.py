from database.db import db
from database.models import ShortlistedCandidate


def rank_and_shortlist(user_id, job_id, ats_results, openings):
    sorted_results = sorted(ats_results, key=lambda item: item.ats_score, reverse=True)
    ShortlistedCandidate.query.filter_by(user_id=user_id, job_id=job_id).delete()
    shortlisted = []
    for rank, result in enumerate(sorted_results[: int(openings or 0)], start=1):
        row = ShortlistedCandidate(
            user_id=user_id,
            job_id=job_id,
            candidate_id=result.candidate_id,
            ats_result_id=result.id,
            rank=rank,
        )
        db.session.add(row)
        shortlisted.append(row)
    db.session.commit()
    return shortlisted

