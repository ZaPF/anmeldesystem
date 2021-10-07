from flask import Flask, current_app, session
from config import config
import logging
from flask_login import AnonymousUserMixin

from . import models


def create_app():
    app = Flask(__name__, template_folder="templates/")

    profile = app.config["ENV"]
    app.config.from_object(config[profile])
    config[profile].init_app(app)
    app.config.from_envvar("ANMELDUNG_SETTINGS", silent=True)

    app.logger.setLevel(logging.DEBUG)

    try:
        logfile = os.path.join(app.config["LOGPATH"], "anmeldesystem_test.log")
        loghandler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=10 ** 4, backupCount=4
        )
        loghandler.setLevel(logging.WARNING)
        app.logger.addHandler(loghandler)
    except:
        pass

    from flask_bootstrap import Bootstrap

    Bootstrap(app)

    from app.oauth_client import oauth_client_blueprint, init_app as init_oauth_client

    app.register_blueprint(oauth_client_blueprint)
    init_oauth_client(app)

    from app.priorities import priorities, init_app as init_priorities

    app.register_blueprint(priorities, url_prefix="/priorities")
    init_priorities(priorities)

    import importlib

    registration = importlib.import_module(f"app.{app.config['CURRENT_REGISTRATION']}")
    app.register_blueprint(registration.reg_blueprint)
    registration.init_app(app)

    @app.context_processor
    def inject_current_user():
        try:
            return dict(current_user=models.User(**session["me"]))
        except:
            return dict(current_user=AnonymousUserMixin())

    return app
