from flask import Flask, current_app
from config import config
import logging

from . import models

def create_app(profile="default"):
    app = Flask(__name__, template_folder='templates/')

    app.config.from_object(config[profile])
    config[profile].init_app(app)
    app.config.from_envvar('ANMELDUNG_SETTINGS', silent=True)

    app.logger.setLevel(logging.DEBUG)

    try:
        logfile = os.path.join(app.config['LOGPATH'], 'anmeldesystem_test.log')
        loghandler = logging.handlers.RotatingFileHandler(logfile, maxBytes=10**4, backupCount=4)
        loghandler.setLevel(logging.WARNING)
        app.logger.addHandler(loghandler)
    except:
        pass

    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    from app.oauth_client import oauth_client_blueprint, init_app as init_oauth_client
    app.register_blueprint(oauth_client_blueprint)
    init_oauth_client(app)

    return app
