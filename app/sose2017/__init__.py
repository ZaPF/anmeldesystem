from flask import Blueprint, session, redirect, url_for

sommer17 = Blueprint('sommer17', __name__, template_folder = 'templates/')

from . import views
def init_app(app):
    return app
