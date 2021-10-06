from flask import Blueprint, session, redirect, url_for
from flask.json import JSONEncoder
from datetime import date

reg_blueprint = Blueprint('sommer20', __name__, template_folder = 'templates/', static_folder = 'static')

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

from . import views
def init_app(app):
    app.json_encoder = CustomJSONEncoder
    return app
