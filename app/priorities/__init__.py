from flask import Blueprint, session, redirect, url_for

priorities = Blueprint(
    "priorities", __name__, template_folder="templates/", static_folder="static"
)

from . import views


def init_app(app):
    return app


@priorities.route("/", methods=["GET", "POST"])
def index():
    pass
