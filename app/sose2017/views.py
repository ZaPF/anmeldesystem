from . import sommer17
from flask import render_template, session, redirect, url_for, flash, current_app, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, validators
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from app.oauth_client import oauth_remoteapp, getOAuthToken, oauth_login_required
import json
from datetime import datetime, time

class BirthdayValidator(object):
    def __call__(self, form, field):
        if(form.exkursion1.data == "stad" or form.exkursion2.data == "stad" or
           form.exkursion3.data == "stad" or form.exkursion4.data == "stad" or
           form.exkursion1.data == "bessy" or form.exkursion2.data == "bessy" or
           form.exkursion3.data == "bessy" or form.exkursion4.data == "bessy"):
            requiredValidator = validators.InputRequired()
            requiredValidator(form, field)
        else:
            optionalValidator = validators.Optional()
            optionalValidator(form, field)

class ExkursionenValidator(object):
    def __init__(self, following=None):
        self.following = following

    def __call__(self, form, field):
        if field.data == "keine":
            for follower in self.following:
                if follower.data != "keine":
                    raise validators.ValidationError('Die folgenden Exkursionen sollten auch auf '
                                                     '"Keine Exkursion" stehen, alles anderes ist '
                                                     'nicht sinnvoll ;).')
        elif field.data != "egal":
            for follower in self.following:
                if follower.data == field.data:
                    raise validators.ValidationError('Selbe Exkursion mehrfach als Wunsch ausgewählt')

class RegistrationPasswordForm(FlaskForm):
    passwort = StringField("Zugangspasswort", [validators.Required()])

class UniTokenForm(FlaskForm):
    passwort = StringField("Token", [validators.Required()])

class Sommer17Registration(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(Sommer17Registration, self).__init__(**kwargs)
        self.exkursion1.validators=[ExkursionenValidator([self.exkursion2, self.exkursion3, self.exkursion4])]
        self.exkursion2.validators=[ExkursionenValidator([self.exkursion3, self.exkursion4])]
        self.exkursion3.validators=[ExkursionenValidator([self.exkursion4])]

    uni = SelectField('Uni', choices=[], coerce=str)
    spitzname = StringField('Spitzname')
    essen = SelectField(u'Essen', choices=[
        ('vegetarisch', 'Vegetarisch'),
        ('vegan', 'Vegan'),
        ('omnivor', 'Omnivor'),
        ])
    allergien = StringField('Allergien')
    heissgetraenk = SelectField('Kaffee oder Tee?', choices=[
        ('egal', 'Egal'),
        ('kaffee', 'Kaffee'),
        ('tee', 'Tee'),
        ])
    getraenk = StringField('Getränkewunsch')
    tshirt = SelectField('T-Shirt', choices=[
        ('keins', 'Nein, ich möchte keins'),
        ('fitted_5xl', 'fitted 5XL'),
        ('fitted_4xl', 'fitted 4XL'),
        ('fitted_3xl', 'fitted 3XL'),
        ('fitted_xxl', 'fitted XXL'),
        ('fitted_xl', 'fitted XL'),
        ('fitted_l', 'fitted L'),
        ('fitted_m', 'fitted M'),
        ('fitted_s', 'fitted S'),
        ('fitted_xs', 'fitted XS'),
        ('5xl', '5XL'),
        ('4xl', '4XL'),
        ('3xl', '3XL'),
        ('xxl', 'XXL'),
        ('xl', 'XL'),
        ('l', 'L'),
        ('m', 'M'),
        ('s', 'S'),
        ('xs', 'XS'),
        ])
    zelten = SelectField('Würdest Du campen wollen?', choices=[
        ('nein', 'nein'),
        ('ja_eigenes_zelt', 'ja, bringe mein eigenes Zelt mit'),
        ('ja_kein_zelt', 'ja, habe aber kein eigenes Zelt.'),
        ])
    exkursionen = [
        ('egal', 'ist mir egal'),
        ('keine', 'keine exkursion'),
        ('mpi', 'Max-Planck-Institut für Kolloid- und Grenzflächenforschung'),
        ('spectrum', 'Technikmuseum und Science Center Spectrum'),
        ('naturkunde', 'Naturkundemuseum'),
        ('bessy', 'Helmholtz-Zentrum Berlin mit BESSY II'),
        ('fub', 'Uni-Tour: Freie Universität Berlin'),
        ('tub', 'Uni-Tour: Technische Universität Berlin'),
        ('golm', 'Uni-Tour: Uni Potsdam in Golm (+ neues Palais)'),
        ('adlershof', 'Wissenschaftscampus Adlershof'),
        ('stad', 'Klassische Stadtführung mit Reichstagsbesichtigung'),
        ('hipster', 'Alternative Stadtführung'),
        ('unterwelten', 'Berliner Unterwelten'),
        ('potsdam', 'Schlösser und Gärten Tour Potsdam'),
        ]

    # Reverse order so the next field can use the variable
    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)

    geburtsdatum = DateField('Geburtsdatum', validators=[BirthdayValidator()])

    alkoholfrei = BooleanField('Ich möchte statt an einer Kneipentour lieber an '
                               'einem alkoholfreien Alternativprogramm in Berlin '
                               'teilnehmen')
    musikwunsch = StringField('Musikwunsch')

    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',
            widget = TextArea())

    orgaprobleme = StringField("Beim ersten Versenden der Einladungen ging leider was schief. " \
            "Deshalb mussten wir sie ein zweites Mal drucken. Was glaubst du, ist passiert?",
            widget = TextArea())

    submit = SubmitField()

def common_error_msg():
    flash("Es ist ein Fehler bei der Abfrage der Daten aufgetreten. Wenn dieser Fehler länger besteht, kontaktiere bitte it@zapf.in-berlin.de", "error")

def handle_zugangspasswort():
    if 'REGISTRATION_PASSWORD' not in current_app.config:
        return None

    if 'zugangspasswort' not in session:
        form = RegistrationPasswordForm()
        if form.validate_on_submit():
            if form.passwort.data.lower() == current_app.config['REGISTRATION_PASSWORD'].lower():
                session['zugangspasswort'] = True
                return redirect(url_for('sommer17.index'))
            else:
                form.passwort.data = ""
                form.passwort.errors.append("Das Zugangspasswort sollte Dir in der Einladung zugeschickt worden sein.")
        return render_template('zugangspasswort.html', form=form)

@sommer17.route('/', methods=['GET', 'POST'])
def index():
    if 'me' not in session:
        return render_template('landing.html')

    form = handle_zugangspasswort()
    if form:
        return form

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login', next = 'index'))

    Form = Sommer17Registration

    defaults = {}
    confirmed = None
    req = oauth_remoteapp.get('registration')
    if req._resp.code == 200:
        defaults = json.loads(req.data['data'])
        if 'geburtsdatum' in defaults and defaults['geburtsdatum']:
            defaults['geburtsdatum'] = datetime.strptime(defaults['geburtsdatum'], "%Y-%m-%d")
        confirmed = req.data['confirmed']

    # Zwischen 6:00 und 7:00
    now = datetime.now().time()
    if time(6,00) <= now <= time(7,00):
        Form = Form.append_field('wach', StringField('Warum bist Du grade wach?',
                widget = TextArea()))
    else:
        defaults.pop('wach', None)

    # Formular erstellen
    form = Form(**defaults)

    # Die Liste der Unis holen
    unis = oauth_remoteapp.get('unis')
    if unis._resp.code != 200:
        return redirect(url_for('oauth_client.login', next = 'index'))
    form.uni.choices = sorted(unis.data.items(), key=lambda uniEntry: int(uniEntry[0]))

    # Daten speichern
    if form.submit.data and form.validate_on_submit():
        req = oauth_remoteapp.post('registration', format='json', data=dict(
            uni_id = form.uni.data, data={k:v for k,v in form.data.items() if k not in ['csrf_token', 'submit']}
            ))
        if req._resp.code == 200 and req.data.decode('utf-8') == "OK":
            flash('Deine Anmeldedaten wurden erfolgreich gespeichert', 'info')
        else:
            flash('Deine Anmeldendaten konnten nicht gespeichert werden.', 'error')
        return redirect('/')

    return render_template('index.html', form=form, confirmed=confirmed)

@sommer17.route('/priorities', methods=['GET', 'POST'])
@oauth_login_required
def priorities():
    if 'me' not in session:
        return redirect('/')

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login', next = 'priorities'))

    if 'uni_token' not in session:
        token_form = UniTokenForm()
        if token_form.validate_on_submit():
            token = token_form.passwort.data
            req = oauth_remoteapp.get('priorities', headers = {'{}'.format(current_app.config['ZAPFAUTH_TOKEN_HEADER']): '{}'.format(token)})
            if req._resp.code == 200:
                session['uni_token'] = token
                return redirect(url_for('sommer17.priorities'))
            else:
                token_form.passwort.data = ""
                token_form.passwort.errors.append("Token scheint nicht korrekt zu sein! Eurer Uni-Token sollte Dir in der Einladung zugeschickt worden sein.")
        return render_template('unitoken.html', form=token_form)

    req = oauth_remoteapp.get('priorities', headers = {'{}'.format(current_app.config['ZAPFAUTH_TOKEN_HEADER']): '{}'.format(session['uni_token'])})
    if req._resp.code != 200:
        common_error_msg()
        return redirect('/')

    registrations = req.data

    return jsonify(registrations)
