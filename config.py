import os
import secrets
from dateutil import parser as dateparser
import pytz

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    FLASK_COVERAGE = 0
    PREFERRED_URL_SCHEME = "https"

    ZAPFAUTH_BASE_URL = getenv("ZAPFAUTH_BASE_URL", "https://auth.zapf.in/api/")
    ZAPFAUTH_AUTHORIZE_URL = getenv("ZAPFAUTH_AUTHORIZE_URL", "https://auth.zapf.in/oauth/authorize")
    ZAPFAUTH_ACCESS_TOKEN_URL = getenv("ZAPFAUTH_ACCESS_TOKEN_URL", "https://auth.zapf.in/oauth/token")
    ZAPFAUTH_REQUEST_TOKEN_URL = None
    ZAPFAUTH_ACCESS_TOKEN_METHOD = "POST"
    ZAPFAUTH_CONSUMER_KEY = os.getenv("ZAPFAUTH_CONSUMER_KEY", "a random string key")
    ZAPFAUTH_CONSUMER_SECRET = os.getenv(
        "ZAPFAUTH_CONSUMER_SECRET", "a random string secret"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_bytes(32))
    ZAPFAUTH_REVOKE_URL = os.getenv("ZAPFAUTH_REVOKE_URL", "https://auth.zapf.in/oauth/revoke")
    ZAPFAUTH_LOGOUT_URL = os.getenv("ZAPFAUTH_LOGOUT_URL", "https://auth.zapf.in/logout")

    CURRENT_REGISTRATION = os.getenv("CURRENT_REGISTRATION", "sose2021")

    TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "Europe/Berlin"))

    REGISTRATION_FORCE_OPEN = "REGISTRATION_FORCE_OPEN" in os.environ
    REGISTRATION_FORCE_PRIORITIES_OPEN = (
        "REGISTRATION_FORCE_PRIORITIES_OPEN" in os.environ
    ) or REGISTRATION_FORCE_OPEN

    REGISTRATION_SOFT_CLOSE = TIMEZONE.localize(
        dateparser.parse(
            os.getenv("REGISTRATION_SOFT_CLOSE", "1970/01/01"), ignoretz=True
        )
    )

    REGISTRATION_HARD_CLOSE = TIMEZONE.localize(
        dateparser.parse(
            os.getenv("REGISTRATION_HARD_CLOSE", "1970/01/01"), ignoretz=True
        )
    )

    ADMIN_USERS = list(
        filter(lambda s: s != "", os.getenv("ADMIN_USERS", "").split(","))
    )

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SECRET_KEY = "secrets"
    PREFERRED_URL_SCHEME = "http"
    DEBUG = True

    @staticmethod
    def init_app(app):
        print("Development config")
        import os

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class ProductionConfig(Config):
    LOGPATH = "logs"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    FLASK_COVERAGE = 1
    SECRET_KEY = "secrets"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
