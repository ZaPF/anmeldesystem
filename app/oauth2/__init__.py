from flask import Blueprint, session, redirect, url_for
from flask_oauthlib.client import OAuth
from functools import wraps

oauth2_blueprint = Blueprint('oauth2', __name__, template_folder = 'templates/')
oauth = OAuth()

oauth_remoteapp = oauth.remote_app(
    'zapfauth',
    base_url='https://auth.zapf.in/api/',
    request_token_url=None,
    access_token_url='https://auth.zapf.in/oauth/token',
    authorize_url='https://auth.zapf.in/oauth/authorize',
    access_token_method='POST',
    request_token_params={'scope': 'ownUserData'},
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
        return redirect(url_for('oauth2.login'))
    return wrapped

from . import views

def init_app(app):
    oauth.init_app(app)
    app.oauth_client = oauth

    # Set up sanity checks.
    from . import sanity
    getattr(app, 'sanity_check_modules', []).append(sanity)

    return app
