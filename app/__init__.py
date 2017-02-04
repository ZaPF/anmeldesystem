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

    # Set up sanity checks.
    from . import sanity
    app.sanity_check_modules = [sanity]

    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    from app.oauth2 import oauth2_blueprint, init_app as init_oauth2
    app.register_blueprint(oauth2_blueprint)
    init_oauth2(app)

    return app

def check_sanity(fix=True):
    # Global sanity checks
    from . import sanity

    sanity_check_modules = getattr(current_app,
            'sanity_check_modules',
            [sanity])
    if sanity not in sanity_check_modules:
        sanity_check_modules.append(sanity)

    for mod in sanity_check_modules:
        current_app.logger.info(
                "Running sanity checks for {mod}".format(mod=mod))
        for i in dir(mod):
            item = getattr(mod,i)
            if callable(item) and i.startswith('check'):
                item(fix)
