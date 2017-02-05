from flask import Blueprint, session, redirect, url_for
from flask_oauthlib.client import OAuth
from functools import wraps

oauth_client_blueprint = Blueprint('oauth_client', __name__, template_folder = 'templates/')
oauth = OAuth()

oauth_remoteapp = oauth.remote_app(
    'zapfauth',
    request_token_params={'scope': 'ownUserData uni_list registration'},
    app_key='ZAPFAUTH'
)

def saveOAuthToken(token, secret):
    session['zapfauth_token'] = (token, secret)

def deleteOAuthToken():
    session.pop('zapfauth_token', None)

@oauth_remoteapp.tokengetter
def getOAuthToken():
    return session.get('zapfauth_token')

def oauth_login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'zapfauth_token' in session:
            return f(*args, **kwargs)
        return redirect(url_for('oauth_client.login'))
    return wrapped

from . import views

def init_app(app):
    oauth.init_app(app)
    app.oauth_client = oauth

    return app
