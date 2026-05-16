from datetime import datetime

from flask_login import UserMixin

from database.db import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(160), nullable=False)
    hr_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    jobs = db.relationship("JobRequirement", backref="user", lazy=True, cascade="all, delete-orphan")


class JobRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    role = db.Column(db.String(160), nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience_required = db.Column(db.Float, default=0)
    openings = db.Column(db.Integer, nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidates = db.relationship("Candidate", backref="job", lazy=True, cascade="all, delete-orphan")
    ats_results = db.relationship("ATSResult", backref="job", lazy=True, cascade="all, delete-orphan")
    shortlisted = db.relationship("ShortlistedCandidate", backref="job", lazy=True, cascade="all, delete-orphan")


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_requirement.id"), nullable=False, index=True)
    name = db.Column(db.String(160))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(80))
    skills = db.Column(db.Text)
    experience = db.Column(db.Float, default=0)
    education = db.Column(db.Text)
    links = db.Column(db.Text)
    resume_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ats_result = db.relationship("ATSResult", backref="candidate", uselist=False, cascade="all, delete-orphan")


class ATSResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_requirement.id"), nullable=False, index=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False, index=True)
    ats_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float, default=0)
    semantic_score = db.Column(db.Float, default=0)
    experience_score = db.Column(db.Float, default=0)
    bonus_score = db.Column(db.Float, default=0)
    missing_skills = db.Column(db.Text)
    status = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ShortlistedCandidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job_requirement.id"), nullable=False, index=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), nullable=False, index=True)
    ats_result_id = db.Column(db.Integer, db.ForeignKey("ats_result.id"), nullable=False, index=True)
    rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidate = db.relationship("Candidate")
    ats_result = db.relationship("ATSResult")


class PasswordResetOTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User")

