from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
from sqlalchemy import func

from auth.auth_routes import auth_bp
from config.settings import Config
from database.db import db, init_db
from database.models import ATSResult, Candidate, JobRequirement, ShortlistedCandidate, User
from services.export_service import export_results
from services.history_service import results_for_job, user_jobs
from services.resume_pipeline import process_resumes

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["EXPORT_FOLDER"]).mkdir(parents=True, exist_ok=True)

    init_db(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)

    @app.template_filter("split_skills")
    def split_skills(value):
        return [item.strip() for item in (value or "").split(",") if item.strip()]

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def landing():
    return render_template("landing.html", title="HireLens AI")


@app.route("/dashboard")
@login_required
def dashboard():
    total_screenings = JobRequirement.query.filter_by(user_id=current_user.id).count()
    total_candidates = Candidate.query.filter_by(user_id=current_user.id).count()
    total_shortlisted = ShortlistedCandidate.query.filter_by(user_id=current_user.id).count()
    avg_score = ATSResult.query.with_entities(func.avg(ATSResult.ats_score)).filter_by(user_id=current_user.id).scalar() or 0
    recent_jobs = user_jobs(current_user.id)[:5]
    return render_template(
        "dashboard.html",
        title="Dashboard",
        total_screenings=total_screenings,
        total_candidates=total_candidates,
        total_shortlisted=total_shortlisted,
        avg_score=round(avg_score, 1),
        recent_jobs=recent_jobs,
    )


@app.route("/new-screening")
@login_required
def new_screening():
    return render_template("new_screening.html", title="New Screening")


@app.route("/process-resumes", methods=["POST"])
@login_required
def process_resumes_route():
    role = (request.form.get("role") or "").strip()
    required_skills = (request.form.get("required_skills") or "").strip()
    openings = request.form.get("openings")
    files = request.files.getlist("resumes")

    if not role or not required_skills or not openings:
        flash("Role, required skills, and number of openings are mandatory.", "error")
        return redirect(url_for("new_screening"))
    try:
        if int(openings) <= 0:
            raise ValueError
    except ValueError:
        flash("Number of openings must be a positive number.", "error")
        return redirect(url_for("new_screening"))
    if not files or not any(file.filename for file in files):
        flash("Upload at least one resume to start screening.", "error")
        return redirect(url_for("new_screening"))

    job, errors = process_resumes(current_user.id, request.form, files)
    for error in errors[:5]:
        flash(error, "warning")
    if Candidate.query.filter_by(user_id=current_user.id, job_id=job.id).count() == 0:
        flash("No resumes could be processed. Please check file contents and try again.", "error")
        return redirect(url_for("new_screening"))
    flash("AI screening completed successfully.", "success")
    return redirect(url_for("results", job_id=job.id))


@app.route("/results/<int:job_id>")
@login_required
def results(job_id):
    job, rows, shortlisted, stats = results_for_job(current_user.id, job_id)
    return render_template(
        "results.html",
        title=f"Results - {job.role}",
        job=job,
        results=rows,
        shortlisted=shortlisted,
        stats=stats,
    )


@app.route("/history")
@login_required
def history():
    jobs = user_jobs(current_user.id)
    stats_by_job = {job.id: results_for_job(current_user.id, job.id)[3] for job in jobs}
    return render_template("history.html", title="History", jobs=jobs, stats_by_job=stats_by_job)


@app.route("/history/<int:job_id>")
@login_required
def history_detail(job_id):
    return redirect(url_for("results", job_id=job_id))


@app.route("/download/all/csv/<int:job_id>")
@login_required
def download_all_csv(job_id):
    path, filename, mimetype = export_results(current_user.id, job_id, scope="all", file_type="csv")
    return send_file(path, as_attachment=True, download_name=filename, mimetype=mimetype)


@app.route("/download/all/excel/<int:job_id>")
@login_required
def download_all_excel(job_id):
    path, filename, mimetype = export_results(current_user.id, job_id, scope="all", file_type="excel")
    return send_file(path, as_attachment=True, download_name=filename, mimetype=mimetype)


@app.route("/download/shortlisted/csv/<int:job_id>")
@login_required
def download_shortlisted_csv(job_id):
    path, filename, mimetype = export_results(current_user.id, job_id, scope="shortlisted", file_type="csv")
    return send_file(path, as_attachment=True, download_name=filename, mimetype=mimetype)


@app.route("/download/shortlisted/excel/<int:job_id>")
@login_required
def download_shortlisted_excel(job_id):
    path, filename, mimetype = export_results(current_user.id, job_id, scope="shortlisted", file_type="excel")
    return send_file(path, as_attachment=True, download_name=filename, mimetype=mimetype)


if __name__ == "__main__":
    app.run(debug=True)

