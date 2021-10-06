from . import reg_blueprint
from flask import render_template, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, validators, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.widgets.html5 import NumberInput
from app.oauth_client import oauth_remoteapp, getOAuthToken
import json
from datetime import datetime, time, timezone
import pytz


T_SHIRT_CHOICES = [
        ('keins', 'Nein, ich möchte keins'),
        ('fitted_xxl', 'XXL fitted'),
        ('fitted_xl', 'XL fitted'),
        ('fitted_l', 'L fitted'),
        ('fitted_m', 'M fitted'),
        ('fitted_s', 'S fitted'),
        ('fitted_xs', 'XS fitted'),
        ('3xl', '3XL'),
        ('xxl', 'XXL'),
        ('xl', 'XL'),
        ('l', 'L'),
        ('m', 'M'),
        ('s', 'S'),
        ('xs', 'XS'),
        ]

HOODIE_CHOICES = [
        ('keins', 'Nein, ich möchte keins'),
        ('3xl', '3XL'),
        ('xxl', 'XXL'),
        ('xl', 'XL'),
        ('l', 'L'),
        ('m', 'M'),
        ('s', 'S'),
        ('xs', 'XS'),
        ]

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

class RegistrationForm(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.exkursion1.validators=[ExkursionenValidator([self.exkursion2, self.exkursion3, self.exkursion4])]
        self.exkursion2.validators=[ExkursionenValidator([self.exkursion3, self.exkursion4])]
        self.exkursion3.validators=[ExkursionenValidator([self.exkursion4])]

    uni = SelectField('Uni', choices=[], coerce=str)
    spitzname = StringField('Spitzname')
    essen = SelectField('Essen', choices=[
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
    essenswunsch = StringField('Unverbindlicher Essenswunsch:')


    exkursionen = [
        ('egal', 'Ist mir egal'),
        ('schwab', 'Weingut Schwab mit Weinprobe und Brotzeit (10€ Selbstbeteiligung)'),
        ('vaqtec', 'va-Q-tec'),
        ('zae', 'Zentrum für angewandte Energieforschung Bayern & Fraunhofer EZRT'),
        ('noell', 'Bilfinger Noell'),
        ('isc', 'Fraunhofer ISC'),
        ('mind','M!ND-Center'),
        ('stfr', 'Stadtführung mit Residenz'),
        ('stff', 'Stadtführung mit Festung Marienberg'),
        ('mft', 'Mainfranken-Theater'),
        ('xray', 'Röntgen-Gedächtnisstätte'),
        ('keine', 'Keine Exkursion'),
       ]
    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)
    musikwunsch = StringField('Musikwunsch')
    alternativprogramm = BooleanField('Ich habe Interesse an einem Alternativprogramm zur Kneipentour')


    anreise = SelectField('Anreise vorraussichtlich mit:', choices=[
        ('bus', 'Fernbus'),
        ('bahn', 'Zug'),
        ('auto', 'Auto'),
        ('flug', 'Flugzeug'),
        ('boot', 'Boot'),
        ('fahrrad', 'Fahrrad'),
        ('zeitmaschine', 'Zeitmaschine'),
        ('badeente', 'Badeente'),
        ])
    anreisejahr =  IntegerField('Anreise aus dem Jahr:', [validators.optional()], widget=NumberInput())
    abreise = SelectField('Abreise vorraussichtlich:', choices=[
        ('ende', 'Nach dem Plenum'),
        ('so810', 'Sonntag 8-10'),
        ('so1012', 'Sonntag 10-12'),
        ('so1214', 'Sonntag 12-14'),
        ('so1416', 'Sonntag 14-16'),
        ('so1618', 'Sonntag 16-18'),
        ('so1820', 'Sonntag 18-20'),
        ('vorso', 'Vor Sonntag'),
        ])
    schlafen = SelectField('Unterkunft', choices=[
        ('egal','Egal'),
        ('MZH','Unterkunft A'),
        ('FW','Unterkunft B'),
        ])
    tshirt = SelectField('T-Shirt', choices = T_SHIRT_CHOICES)
    addtshirt = IntegerField('Anzahl zusätzliche T-Shirts',[validators.optional()], widget=NumberInput())
    hoodie = SelectField('Hoodie', choices = HOODIE_CHOICES)
    handtuch = BooleanField('Ich möchte gerne ein Handtuch bestellen')
    roemer = BooleanField('Ich möchte gerne einen Weinrömer bestellen')
    minderjaehrig = BooleanField('Ich bin zum Zeitpunkt der ZaPF JÜNGER als 18 Jahre.')
    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',


#    gremien = BoolanField('Ich bin Mitglied in StAPF, TOPF, KommGrem, oder ZaPF-e.V-Vorstand und moechte mich über das Gremienkontingent anmelden.')





            widget = TextArea())

    submit = SubmitField()

@reg_blueprint.route('/', methods=['GET', 'POST'])
def index():
    registration_open = (datetime.now(pytz.utc) <= current_app.config['REGISTRATION_SOFT_CLOSE']) or current_app.config['REGISTRATION_FORCE_OPEN']
    priorities_open   = (datetime.now(pytz.utc) <= current_app.config['REGISTRATION_HARD_CLOSE']) or current_app.config['REGISTRATION_FORCE_PRIORITIES_OPEN']
    is_admin = 'me' in session and session['me']['username'] in current_app.config['ADMIN_USERS']

    if not is_admin and not priorities_open:
        return render_template('registration_closed.html')

    if 'me' not in session:
        return render_template('landing.html', registration_open = registration_open, priorities_open = priorities_open)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = RegistrationForm

    defaults = {}
    confirmed = None
    req = oauth_remoteapp.get('registration')
    if req._resp.code == 200:
        defaults = json.loads(req.data['data'])
        if 'geburtsdatum' in defaults and defaults['geburtsdatum']:
            defaults['geburtsdatum'] = datetime.strptime(defaults['geburtsdatum'], "%Y-%m-%d")
        confirmed = req.data['confirmed']
    else:
        if not is_admin and not registration_open:
            return render_template('registration_closed.html')

    # Formular erstellen
    form = Form(**defaults)

    # Die Liste der Unis holen
    unis = oauth_remoteapp.get('unis')
    if unis._resp.code != 200:
        return redirect(url_for('oauth_client.login'))
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

@reg_blueprint.route('/admin/wise18/<string:username>', methods=['GET', 'POST'])
def adminEdit(username):
    if 'me' not in session:
        return redirect('/')

    is_admin = 'me' in session and session['me']['username'] in current_app.config['ADMIN_USERS']
    if not is_admin:
        abort(403)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = RegistrationForm

    defaults = {}
    confirmed = None
    req = oauth_remoteapp.get('registration', data={'username': username})
    if req._resp.code == 200:
        defaults = json.loads(req.data['data'])
        if 'geburtsdatum' in defaults and defaults['geburtsdatum']:
            defaults['geburtsdatum'] = datetime.strptime(defaults['geburtsdatum'], "%Y-%m-%d")
        confirmed = req.data['confirmed']
    elif req._resp.code == 409:
        flash('Username is unknown', 'error')
        return redirect('/')

    # Formular erstellen
    form = Form(**defaults)

    # Die Liste der Unis holen
    unis = oauth_remoteapp.get('unis')
    if unis._resp.code != 200:
        return redirect(url_for('oauth_client.login'))
    form.uni.choices = sorted(unis.data.items(), key=lambda uniEntry: int(uniEntry[0]))

    # Daten speichern
    if form.submit.data and form.validate_on_submit():
        req = oauth_remoteapp.post('registration', format='json', data=dict(username = username,
            uni_id = form.uni.data, data={k:v for k,v in form.data.items() if k not in ['csrf_token', 'submit']}
            ))
        if req._resp.code == 200 and req.data.decode('utf-8') == "OK":
            flash('Deine Anmeldedaten wurden erfolgreich gespeichert', 'info')
        else:
            flash('Deine Anmeldendaten konnten nicht gespeichert werden.', 'error')
        return redirect(url_for('reg_blueprint.adminEdit', username=username))

    return render_template('index.html', form=form, confirmed=confirmed)
