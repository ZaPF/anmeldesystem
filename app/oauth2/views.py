from flask import redirect, url_for, request, jsonify
from . import oauth2_blueprint, oauth_remoteapp, saveOAuthToken, getOAuthToken, deleteOAuthToken, oauth_login_required

@oauth2_blueprint.route('/oauth/login')
def login():
    return oauth_remoteapp.authorize(callback=url_for('oauth2.authorized', _external=True))

@oauth2_blueprint.route('/oauth/authorized')
def authorized():
    resp = oauth_remoteapp.authorized_response()
    if resp is None or resp.get('access_token') is None:
        print('Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        ))
        return redirect('/')
    saveOAuthToken(resp['access_token'], '')
    return redirect('/')

@oauth2_blueprint.route('/oauth/logout')
def logout():
    deleteOAuthToken()
    return redirect('/')

@oauth2_blueprint.route('/')
@oauth_login_required
def index():
    me = oauth_remoteapp.get('me')
    return jsonify(res = me.data)
