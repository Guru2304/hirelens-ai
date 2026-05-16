import re
from html import escape

from auth.password_service import validate_password_strength

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def sanitize(value):
    return escape((value or "").strip())


def validate_email(email):
    return bool(EMAIL_RE.match((email or "").strip()))


def validate_password(password):
    return validate_password_strength(password)


def validate_otp(otp):
    return bool(re.fullmatch(r"\d{6}", (otp or "").strip()))

