from flask import Blueprint, current_app, redirect, url_for, make_response, request
from flask_oauthlib.client import OAuth
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.contrib.securecookie import SecureCookie

oauth_client_blueprint = Blueprint('oauth_client', __name__, template_folder = 'templates/')
oauth = OAuth()

oauth_remoteapp = oauth.remote_app(
    'zapfauth',
    request_token_params={'scope': 'ownUserData uni_list registration registration_priorities'},
    app_key='ZAPFAUTH'
)

def saveOAuthToken(next, token, secret, max_age = 3000):
    secretKey = current_app.config['SECRET_KEY'].encode('utf-8')
    data = SecureCookie({"token": token, "secret": secret}, secretKey)
    expires = datetime.utcnow() + timedelta(seconds = max_age)
    resp = make_response(next)
    resp.set_cookie('zapfauth_token', data.serialize(), expires = expires)
    return resp

def deleteOAuthToken(next):
    resp = make_response(next)
    resp.set_cookie('zapfauth_token', '', expires = 0)
    return resp

@oauth_remoteapp.tokengetter
def getOAuthToken():
    secretKey = current_app.config['SECRET_KEY'].encode('utf-8')
    cookie = request.cookies.get('zapfauth_token')
    if not cookie:
        return None
    data = SecureCookie.unserialize(cookie, secretKey)
    return (data["token"], data["secret"])

def oauth_login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not getOAuthToken():
            return redirect(url_for('oauth_client.login'))
        return f(*args, **kwargs)
    return wrapped

from . import views

def init_app(app):
    oauth.init_app(app)
    app.oauth_client = oauth

    return app
