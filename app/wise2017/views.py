from . import winter17
from flask import render_template, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, validators
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from app.oauth_client import oauth_remoteapp, getOAuthToken
import json
from datetime import datetime, time, timezone
import pytz

REGISTRATION_SOFT_CLOSE = datetime(2017, 9, 30, 21, 59, 59, tzinfo=pytz.utc)
REGISTRATION_HARD_CLOSE = datetime(2017, 10, 3, 21, 59, 59, tzinfo=pytz.utc)
ADMIN_USER = ['pjaeger', 'Helena', 'Benedikt', 'EnteEnte', 'Lina', 'benni']

T_SHIRT_CHOICES = [
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

class Winter17Registration(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(Winter17Registration, self).__init__(**kwargs)
        self.exkursion1.validators=[ExkursionenValidator([self.exkursion2, self.exkursion3, self.exkursion4])]
        self.exkursion2.validators=[ExkursionenValidator([self.exkursion3, self.exkursion4])]
        self.exkursion3.validators=[ExkursionenValidator([self.exkursion4])]

    uni = SelectField('Uni', choices=[], coerce=str)
    spitzname = StringField('Spitzname')
    addx = BooleanField('@ &sum; x')
    schlafen = SelectField('Schlafgewohnheiten', choices=[
        ('nachteule','Nachteule'),
        ('morgenmuffel','Morgenmuffel'),
        ('vogel','Früher Vogel'),
        ])
    essen = SelectField('Essen', choices=[
        ('vegetarisch', 'Vegetarisch'),
        ('vegan', 'Vegan'),
        ('omnivor', 'Omnivor'),
        ])
    mittag1 = SelectField('Mittagessen Sonntag', choices=[
        ('normal','Schnitzel mit Rahmsoße'),
        ('vegan','Gemüseschnitzel mit Kräutersoße'),
        ])
    mittag2 = SelectField('Mittagessen Montag', choices=[
        ('normal','Hähnchen mit Nudeln'),
        ('vegan','Sojaschnitzel mit Nudeln'),
        ])

    mittag3 = SelectField('Mittagessen Dienstag', choices=[
        ('normal','Currywurst'),
        ('vegan','veg. Currywurst'),
        ])


    allergien = StringField('Allergien')
    heissgetraenk = SelectField('Kaffee oder Tee?', choices=[
        ('egal', 'Egal'),
        ('kaffee', 'Kaffee'),
        ('tee', 'Tee'),
        ])
    getraenk = StringField('Getränkewunsch')
    tshirt = SelectField('T-Shirt', choices = T_SHIRT_CHOICES)
    muetze = BooleanField('Ich möchte gerne eine Mütze haben')
    #Erklaertext: Kosten unter 7 EUR. Verbindliche Kaufzusage.
    hoodie = SelectField('Hoodie', choices = T_SHIRT_CHOICES)
    #Erklaertext: Kosten ca. 20 EUR. Verbindliche Kaunzusage.
    anreise = SelectField('Anreise vorraussichtlich mit:', choices=[
        ('bus', 'Fernbus'),
        ('bahn', 'Zug'),
        ('auto', 'Auto'),
        ('flug', 'Flugzeug'),
        ('fahrrad', 'Fahrrad'),
        ('einhorn', 'Einhorn'),
        ('uboot', 'U-Boot'),
        ])
#    gremien = BoolanField('Ich bin Mitglied in StAPF, TOPF, KommGrem, oder ZaPF-e.V-Vorstand und moechte mich über das Gremienkontingent anmelden.')
    workshop = BooleanField('Ich plane, bereits mittwochs vormittags abzureisen')
    exkursionen = [
        ('egal', 'ist mir egal'),
        ('keine', 'keine exkursion'),
        ('ipg', 'IPG Photonics'),
        ('nch', 'Neurochirurgie'),
        ('km', 'Krueckemeyer Klebstoffe'),
        ('ejot', 'EJOT Schrauben'),
        ('lennestadt', 'Sauerland-Pyramiden'),
        ('vbsi', 'Versorgungsbetriebe Siegen'),
        ('fokos', 'FoKoS'),
#        ('staudamm', 'Staudamm'),
        ('bwf', 'Bergwerksfuehrung'),
        ('stf', 'Stadtführung'),
        ('wandern', 'Wandern'),
        ('lan', 'LAN Party'),
        ]

    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)

    musikwunsch = StringField('Musikwunsch')

    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',
            widget = TextArea())

    submit = SubmitField()

@winter17.route('/', methods=['GET', 'POST'])
def index():
    registration_open = datetime.now(pytz.utc) <= REGISTRATION_SOFT_CLOSE
    priorities_open   = datetime.now(pytz.utc) <= REGISTRATION_HARD_CLOSE
    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER

    if not is_admin and not priorities_open:
        return render_template('registration_closed.html')

    if 'me' not in session:
        return render_template('landing.html', registration_open = registration_open, priorities_open = priorities_open)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = Winter17Registration

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

@winter17.route('/admin/wise17/<string:username>', methods=['GET', 'POST'])
def adminEdit(username):
    if 'me' not in session:
        return redirect('/')

    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER
    if not is_admin:
        abort(403)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = Winter17Registration

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
        return redirect(url_for('sommer17.adminEdit', username=username))

    return render_template('index.html', form=form, confirmed=confirmed)
