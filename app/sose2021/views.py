
# coding=utf-8
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

REGISTRATION_SOFT_CLOSE = datetime(2021, 5, 23, 21, 59, 59, tzinfo=pytz.utc)
REGISTRATION_HARD_CLOSE = datetime(2021, 5, 24, 21, 59, 59, tzinfo=pytz.utc)
ADMIN_USER = ['justus2342','Hobbesgoblin']

T_SHIRT_CHOICES = [
        ('keins', 'Nein, ich möchte keins'),
        ('fitted_xxl', 'XXL fitted'),
       ('fitted_xl', 'XL fitted'),
       ('fitted_l', 'L fitted'),
        ('fitted_m', 'M fitted'),
        ('fitted_s', 'S fitted'),
        ('fitted_xs', 'XS fitted'),
#        ('5xl', '5XL'),
#        ('4xl', '4XL'),
        ('3xl', '3XL'),
        ('xxl', 'XXL'),
        ('xl', 'XL'),
        ('l', 'L'),
        ('m', 'M'),
        ('s', 'S'),
        ('xs', 'XS'),
        ]

HOODIE_CHOICES = [
        ('keins', 'Nein, ich möchte keinen'),
        ('fitted_xxl', 'XXL fitted'),
       ('fitted_xl', 'XL fitted'),
       ('fitted_l', 'L fitted'),
        ('fitted_m', 'M fitted'),
        ('fitted_s', 'S fitted'),
        ('fitted_xs', 'XS fitted'),
#        ('5xl', '5XL'),
#        ('4xl', '4XL'),
        ('3xl', '3XL'),
        ('xxl', 'XXL'),
        ('xl', 'XL'),
        ('l', 'L'),
        ('m', 'M'),
        ('s', 'S'),
        ('xs', 'XS'),
        ]


MERCH_COLORS = [
        ('navy','Navy'),
        ('grau','Dunkelgrau'),
        ('schwarz','Schwarz'),
        ]

class RegistrationForm(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)

    uni = SelectField('Uni', choices=[], coerce=str)
    spitzname = StringField('Spitzname')
    
    musikwunsch = StringField('Musikwunsch')

    anreise_verkehr = SelectField('Wie wärst Du zur Ostsee-ZaPF gereist?', choices=[
        ('bus', 'Fernbus'),
        ('bahn', 'Zug'),
        ('auto', 'Auto'),
#        ('flug', 'Flugzeug'),
        ('zeitmaschine', 'Zeitmaschine'),
        ('boot', 'Boot'),
        ('fahrrad', 'Fahrrad'),
        ('badeente', 'Badeente'),
        ])
    tshirt = SelectField('Ich möchte gerne ein T-Shirt für max. 17 Euro bestellen.', choices = T_SHIRT_CHOICES)
    tshirt_color = SelectField('Als T-Shirt-Farbe möchte ich', choices = MERCH_COLORS)
    addtshirt = IntegerField('Anzahl zusätzliche T-Shirts',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())




    hoodie = SelectField('Ich möchte gerne einen Hoodie für max. 30 Euro bestellen', choices = HOODIE_CHOICES)
    hoodie_color = SelectField('Als Hoodie-Farbe möchte ich', choices = MERCH_COLORS)
    handtuch = IntegerField('Anzahl Handtuch (max. 12 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())
    tasse = IntegerField('Anzahl Tassen (max. 10 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())
    usb = IntegerField('Anzahl USB-Stick (max. 6 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())
    frisbee = IntegerField('Anzahl Frisbee (max. 22 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())
    aufnaeher = IntegerField('Anzahl Aufnäher (max. 10 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())
    schal = IntegerField('Anzahl Schlauchschal (max. 10 Euro pro Stück)',[validators.NumberRange(min=0),validators.optional()], widget=NumberInput())

    zaepfchen = SelectField('Kommst Du zum ersten Mal zu einer ZaPF?', choices=[
        ('ja','Ja'),
        ('jaund','Ja und ich hätte gerne ein ZaPF-Mentikon.'),
        ('nein','Nein'),
        ])
    mentor = BooleanField('Ich möchte ZaPF-Mentikon werden und erkläre mich damit einverstanden, dass meine E-Mail-Adresse an ein Zäpfchen weitergegeben wird.')
    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',
    widget = TextArea())
    submit = SubmitField()




    vertrauensperson = SelectField('Wärst Du bereit, dich als Vertrauensperson aufzustellen? (Du weißt nicht was das ist? Gib bitte "Nein" an!)', choices=[
	    ('nein', 'Nein'),
	    ('ja', 'Ja'),
    ])
    protokoll = SelectField('Wärst Du bereit bei den Plenen Protokoll zu schreiben?', choices=[
            ('nein', 'Nein'),
            ('ja','Ja'),
    ])
    schwimmabzeichen = SelectField('Welches Schwimmabzeichen hast Du?', choices=[
        ('keins','keins'),
        ('bleiente','Bleiente'),
        ('seepferd','Seepferdchen'),
        ('bronze','Bronze'),
        ('silber','Silber'),
        ('gold','Gold'),
        ('rett','Rettungsschwimmer*in'),
    ])


@reg_blueprint.route('/', methods=['GET', 'POST'])
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
    if unis._resp.code == 500:
        raise
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

@reg_blueprint.route('/admin/sose21/<string:username>', methods=['GET', 'POST'])
def adminEdit(username):
    if 'me' not in session:
        return redirect('/')

    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER
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


