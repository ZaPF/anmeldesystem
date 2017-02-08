from flask import redirect, url_for, request, jsonify, session, current_app, flash
from . import oauth_client_blueprint, oauth_remoteapp, saveOAuthToken, getOAuthToken, deleteOAuthToken, oauth_login_required
try:
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qsl, ParseResult
except ImportError:
    from urllib.parse import urlencode, unquote, urlparse, parse_qsl, ParseResult


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url

@oauth_client_blueprint.route('/oauth/login')
def login():
    return oauth_remoteapp.authorize(callback=url_for('oauth_client.authorized', _external=True))

@oauth_client_blueprint.route('/oauth/authorized')
def authorized():
    resp = oauth_remoteapp.authorized_response()
    if resp is None or resp.get('access_token') is None:
        flash('Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        ), 'error')
        return redirect('/')
    if 'me' not in session:
        next = redirect(url_for('oauth_client.loadMe'))
    else:
        next = redirect('/')
    return saveOAuthToken(next, resp['access_token'], '')

@oauth_client_blueprint.route('/oauth/logout')
def logout():
    oauth_remoteapp.post(current_app.config["ZAPFAUTH_REVOKE_URL"])
    session.clear()
    return deleteOAuthToken(redirect(add_url_params(current_app.config["ZAPFAUTH_LOGOUT_URL"],
             {"next": url_for('oauth_client.loggedout', _external=True)})))

@oauth_client_blueprint.route('/oauth/loadme')
def loadMe():
    session['me'] = oauth_remoteapp.get('me').data
    return redirect('/')

@oauth_client_blueprint.route('/oauth/loggedout')
def loggedout():
    flash("Du wurdest erfolgreich abgemeldet!", "info")
    return redirect('/')
