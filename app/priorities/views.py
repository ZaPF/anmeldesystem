from . import priorities
from flask import render_template, session, redirect, url_for, flash, current_app
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from functools import wraps
from datetime import datetime
import pytz

class TokenException(Exception):
    pass

class TokenForm(FlaskForm):
    password = StringField("Token", [validators.Required()])

class MascotForm(FlaskForm):
    name = StringField('Name des Maskottchens', [validators.Required()])
    submit = SubmitField()

def get_registrations(token):
    s = requests.Session()

    s.headers.update({'Authorization': 'ZaPF-Token %s' % token})

    r = s.get(current_app.config['ZAPFAUTH_BASE_URL'] + 'priorities')

    if r.status_code == 401:
        raise TokenException()
    elif r.status_code != 200:
        raise Exception()

    return r.json()


def post_registrations(token, priorities):
    s = requests.Session()
    s.headers.update({'Authorization': 'ZaPF-Token %s' % token})

    r = s.post(current_app.config['ZAPFAUTH_BASE_URL'] + 'priorities', json={'confirmed': priorities})

    if r.status_code == 401:
        raise TokenException()
    elif r.status_code != 200:
        raise Exception()

def get_mascots(token):
    s = requests.Session()
    s.headers.update({'Authorization': 'ZaPF-Token %s' % token})

    r = s.get(current_app.config['ZAPFAUTH_BASE_URL'] + 'mascots')

    if r.status_code == 401:
        raise TokenException()
    elif r.status_code != 200:
        raise Exception()

    return r.json()

def post_mascot(token, name):
    s = requests.Session()
    s.headers.update({'Authorization': 'ZaPF-Token %s' % token})

    r = s.post(current_app.config['ZAPFAUTH_BASE_URL'] + 'mascots', json={'name': name})

    if r.status_code == 401:
        raise TokenException()
    elif r.status_code != 200:
        raise Exception()

def get_token():
    form = TokenForm();
    if form.validate_on_submit():
        token = form.password.data # FIXME: escape

        try:
            _ = get_registrations(token)
        except TokenException:
            form.password.data = ""
            form.password.errors.append("Der angegebene Uni-Token ist falsch. Euer Uni-Token sollte Euch in der Einladung zugeschickt worden sein.")
        except:
            raise
        else:
            session['zapf_token'] = token
            return redirect(url_for('priorities.index'))

    return render_template('token.html', form=form)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'zapf_token' not in session:
            return get_token()
        return f(*args, **kwargs)
    return decorated_function

def check_if_closed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        REGISTRATION_HARD_CLOSE = datetime(2019, 9, 13, 21, 59, 59, tzinfo=pytz.utc)
        if datetime.now(pytz.utc) > REGISTRATION_HARD_CLOSE:
            return render_template("priorities_closed.html")
        return f(*args, **kwargs)
    return decorated_function

@priorities.route('/', methods=['GET', 'POST'])
@check_if_closed
@token_required
def priorities_index():
    registrations = get_registrations(session['zapf_token'])
    confirmed = [registration for registration in registrations['registrations'] if registration['priority'] is not None]
    unconfirmed = [registration for registration in registrations['registrations'] if registration['priority'] is None]
    mascots = get_mascots(session['zapf_token'])
    return render_template("priorities.html",
            uni=registrations['uni'],
            slots=registrations['slots'],
            confirmed=confirmed,
            unconfirmed=unconfirmed,
            mascots=mascots['mascots'])

@priorities.route('/mascot/new', methods=['GET', 'POST'])
@check_if_closed
@token_required
def add_mascot():
    form = MascotForm()

    if form.validate_on_submit():
        post_mascot(session['zapf_token'],form.name.data)
        return redirect(url_for('priorities.index'))
    return render_template('newmascot.html', form = form)


@priorities.route('/mascot/delete/<int:id>', methods=['GET', 'POST'])
@check_if_closed
@token_required
def del_mascot(id):
    s = requests.Session()
    s.headers.update({'Authorization': 'ZaPF-Token %s' % session['zapf_token']})

    r = s.post(current_app.config['ZAPFAUTH_BASE_URL'] + 'mascots/delete', json={'id': id})

    if r.status_code == 401:
        raise TokenException()
    elif r.status_code != 200:
        raise Exception()

    return redirect(url_for('priorities.index'))

def _generate_post_payload(priorities_dict):
    """
    Generate a list of priorities from a dictionary of the form {reg_id:prioritiy}
    """
    return sorted(
            [k for k in priorities_dict
                if priorities_dict[k] is not None
                and priorities_dict[k] != -1],
            key=lambda k: priorities_dict[k] or 0
            )


def priority_modifier(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        priorities = {
                reg['reg_id']: reg['priority']
                for reg in get_registrations(session['zapf_token'])['registrations']
                }

        post_registrations(session['zapf_token'],
                _generate_post_payload(f(*args, priorities=priorities, **kwargs)))

        return redirect(url_for('priorities.index'))

    return decorated_function


@priorities.route('/confirm/<int:id>')
@check_if_closed
@token_required
@priority_modifier
def confirm(id, priorities={}):
    if priorities[id] == -1:
        flash('Garantierte Plätze müssen nicht bestätigt werden.')
        return priorities

    # set the confirmed registration's priority to the maximum (i.e. last) priority
    priorities.update({id: max([v if v else 0 for v in priorities.values()])+1})
    return priorities


@priorities.route('/unconfirm/<int:id>')
@check_if_closed
@token_required
@priority_modifier
def unconfirm(id, priorities={}):
    if priorities[id] == -1:
        flash('Garantierte Plätze können nicht entfernt werden.')
        return priorities

    priorities.update({id: None})
    return priorities


@priorities.route('/increase/<int:id>')
@check_if_closed
@token_required
@priority_modifier
def increase(id, priorities={}):
    if priorities[id] == 0:
        flash('Das ist schon die höchste Priorität...')
        return priorities
    elif priorities[id] == -1:
        flash('Garantierte Plätze können nicht umpriorisiert werden.')
        return priorities

    #To increase the priority, swap with the item directly above.
    id_above = {priority: id for id, priority in priorities.items()}[priorities[id]-1]
    priorities[id], priorities[id_above] = priorities[id_above], priorities[id]

    return priorities

@priorities.route('/decrease/<int:id>')
@check_if_closed
@token_required
@priority_modifier
def decrease(id, priorities={}):
    if priorities[id] == max([v if v else 0 for v in priorities.values()]):
        flash('Das ist schon die niedrigste Priorität...')
        return priorities
    elif priorities[id] == -1:
        flash('Garantierte Plätze können nicht umpriorisiert werden.')
        return priorities

    #To increase the priority, swap with the item directly below.
    id_below = {priority: id for id, priority in priorities.items()}[priorities[id]+1]
    priorities[id], priorities[id_below] = priorities[id_below], priorities[id]

    return priorities

@priorities.route("/logout")
def logout():
    session.pop('zapf_token', None)
    return redirect(url_for('priorities.index'))
