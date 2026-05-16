from pathlib import Path
from uuid import uuid4

import pandas as pd
from flask import current_app

from services.history_service import results_for_job


def _all_rows(results):
    rows = []
    for result in results:
        candidate = result.candidate
        rows.append(
            {
                "Candidate Name": candidate.name,
                "Email": candidate.email,
                "Phone": candidate.phone,
                "Skills": candidate.skills,
                "Experience": candidate.experience,
                "Education": candidate.education,
                "Links": candidate.links,
                "ATS Score": result.ats_score,
                "Skills Score": result.skills_score,
                "Semantic Score": result.semantic_score,
                "Experience Score": result.experience_score,
                "Bonus Score": result.bonus_score,
                "Missing Skills": result.missing_skills,
                "Status": result.status,
            }
        )
    return rows


def _shortlisted_rows(shortlisted):
    rows = []
    for item in shortlisted:
        candidate = item.candidate
        result = item.ats_result
        rows.append(
            {
                "Rank": item.rank,
                "Candidate Name": candidate.name,
                "Email": candidate.email,
                "ATS Score": result.ats_score,
                "Key Skills": candidate.skills,
                "Status": result.status,
            }
        )
    return rows


def export_results(user_id, job_id, scope="all", file_type="csv"):
    job, results, shortlisted, _stats = results_for_job(user_id, job_id)
    rows = _all_rows(results) if scope == "all" else _shortlisted_rows(shortlisted)
    df = pd.DataFrame(rows)
    export_dir = Path(current_app.config["EXPORT_FOLDER"])
    export_dir.mkdir(parents=True, exist_ok=True)
    suffix = "xlsx" if file_type == "excel" else "csv"
    filename = f"hirelens_{scope}_{job.id}_{uuid4().hex[:8]}.{suffix}"
    path = export_dir / filename
    if suffix == "xlsx":
        df.to_excel(path, index=False)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        df.to_csv(path, index=False)
        mimetype = "text/csv"
    return path, filename, mimetype

