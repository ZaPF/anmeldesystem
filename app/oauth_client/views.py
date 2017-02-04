from flask import redirect, url_for, request, jsonify, session
from . import oauth_client_blueprint, oauth_remoteapp, saveOAuthToken, getOAuthToken, deleteOAuthToken, oauth_login_required

@oauth_client_blueprint.route('/oauth/login')
def login():
    return oauth_remoteapp.authorize(callback=url_for('oauth_client.authorized', _external=True))

@oauth_client_blueprint.route('/oauth/authorized')
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
    session['me'] = oauth_remoteapp.get('me').data
    return redirect('/')

@oauth_client_blueprint.route('/oauth/logout')
def logout():
    deleteOAuthToken()
    session.clear()
    return redirect('/')
