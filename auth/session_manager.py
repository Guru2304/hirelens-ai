from flask import current_app
from flask_login import login_user


def login_hr(user, remember=False):
    duration = current_app.config.get("REMEMBER_COOKIE_DURATION")
    login_user(user, remember=remember, duration=duration)

