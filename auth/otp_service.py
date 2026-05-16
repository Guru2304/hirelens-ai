import random
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import MAX_OTP_ATTEMPTS, OTP_EXPIRY_MINUTES
from database.db import db
from database.models import PasswordResetOTP, User


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def store_otp(user, otp):
    PasswordResetOTP.query.filter_by(user_id=user.id, is_used=False).update({"is_used": True})
    record = PasswordResetOTP(
        user_id=user.id,
        email=user.email,
        otp_hash=generate_password_hash(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.session.add(record)
    db.session.commit()
    return record


def verify_otp(email, otp):
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "Account not found."

    record = (
        PasswordResetOTP.query.filter_by(user_id=user.id, email=email, is_used=False)
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )
    if not record:
        return False, "No active OTP found. Please request a new code."
    if record.expires_at < datetime.utcnow():
        record.is_used = True
        db.session.commit()
        return False, "OTP expired. Please request a new code."
    if record.attempts >= MAX_OTP_ATTEMPTS:
        record.is_used = True
        db.session.commit()
        return False, "Too many incorrect attempts. Please request a new code."

    record.attempts += 1
    if not check_password_hash(record.otp_hash, otp):
        db.session.commit()
        return False, "Incorrect OTP."

    record.is_used = True
    db.session.commit()
    return True, "OTP verified."

