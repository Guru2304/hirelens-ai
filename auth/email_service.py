from flask import current_app
from flask_mail import Message


def send_otp_email(mail, recipient, otp, expiry_minutes):
    if not current_app.config.get("MAIL_USERNAME") or not current_app.config.get("MAIL_PASSWORD"):
        current_app.logger.warning("Mail credentials are not configured. OTP for %s is %s", recipient, otp)
        return False, "Email credentials are not configured. Check server logs for development OTP."

    body = (
        "Hello,\n\n"
        f"Your HireLens AI password reset OTP is {otp}.\n"
        f"This code expires in {expiry_minutes} minutes and can be used only once.\n\n"
        "If you did not request this, you can safely ignore this email.\n\n"
        "HireLens AI"
    )
    try:
        msg = Message(
            subject="Your HireLens AI Password Reset OTP",
            recipients=[recipient],
            body=body,
        )
        mail.send(msg)
        return True, "OTP sent successfully."
    except Exception as exc:
        current_app.logger.exception("Failed to send OTP email")
        return False, f"Unable to send OTP email: {exc}"

