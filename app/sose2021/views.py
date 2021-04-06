
# coding=utf-8
from . import sommer21
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

REGISTRATION_SOFT_CLOSE = datetime(2021, 5, 12, 21, 59, 59, tzinfo=pytz.utc)
REGISTRATION_HARD_CLOSE = datetime(2021, 5, 12, 21, 59, 59, tzinfo=pytz.utc)
ADMIN_USER = ['justus2342','Hobbesgoblin']

T_SHIRT_CHOICES = [
        ('keins', 'Nein, ich möchte keins'),
#        ('fitted_xxl', 'XXL fitted'),
#       ('fitted_xl', 'XL fitted'),
#       ('fitted_l', 'L fitted'),
#        ('fitted_m', 'M fitted'),
#        ('fitted_s', 'S fitted'),
#        ('fitted_xs', 'XS fitted'),
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
#        ('fitted_xxl', 'XXL fitted'),
#       ('fitted_xl', 'XL fitted'),
#       ('fitted_l', 'L fitted'),
#        ('fitted_m', 'M fitted'),
#        ('fitted_s', 'S fitted'),
#        ('fitted_xs', 'XS fitted'),
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

class ImmatrikulationsValidator(object):
	def __init__(self, following=None):
		self.following = following

	def __call__(self, form, field):
		if field.data != 'ja' and field.data != 'n.i.':
			raise validators.ValidationError('Bitte gib an, dass du deine Immatrikulationsbescheinigung mitbringen wirst oder, dass du keine hast.')

class ImmatrikulationsValidator2(object):
	def __init__(self, following=None):
		self.following = following

	def __call__(self, form, field):
		if field.data != 'nein' and field.data != 'n.i.':
			raise validators.ValidationError('Bitte gib an, dass du deine Immatrikulationsbescheinigung nicht vergessen wirst.')



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

class Sommer21Registration(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(Sommer21Registration, self).__init__(**kwargs)
        self.exkursion1.validators=[ExkursionenValidator([self.exkursion2, self.exkursion3, self.exkursion4])]
        self.exkursion2.validators=[ExkursionenValidator([self.exkursion3, self.exkursion4])]
        self.exkursion3.validators=[ExkursionenValidator([self.exkursion4])]
        self.immatrikulationsbescheinigung.validators=[ImmatrikulationsValidator(self.immatrikulationsbescheinigung)]
        self.immatrikulationsbescheinigung2.validators=[ImmatrikulationsValidator2(self.immatrikulationsbescheinigung2)]

    uni = SelectField('Uni', choices=[], coerce=str)
    spitzname = StringField('Spitzname')
    ])


    essen = SelectField('Essen', choices=[
        ('omnivor', 'Omnivor'),
        ('vegetarisch', 'Vegetarisch'),
        ('vegan', 'Vegan'),
        ])
    allergien = StringField('Allergien')
    heissgetraenk = SelectField('Kaffee oder Tee?', choices=[
#        ('egal', 'Egal'),
        ('kaffee', 'Kaffee'),
        ('tee', 'Tee'),
        ])
#   essenswunsch = StringField('Unverbindlicher Essenswunsch:')

    exkursionen = [
        ('keine', 'keine Exkursion'),#
        ('egal', 'Ist mir egal'),#
        ('alpaka', 'Alpakawanderung, 15 Euro'),#
        ('ente', 'Entennähworkshop, 1 Euro'),#
        ('hansebrau', 'Hanseatische Brauerei, 8 Euro'),#
        ('iow', 'Institut für Ostseeforschung'),#
        ('kulturhist', 'Kulturhistorisches Museum'),#
        ('laser','Lasertag, 20 Euro'),#
        ('inp', 'Leibniz-Institut für Plasmaforschung und Technologie, Greifswald'),#
        ('ipp', 'Max-Planck-Institut für Plasmaphysik, Greifswald'),#
        ('physch', 'PhySch-Labor'),#
        ('stadt','Stadtführung'),#
        ('strand', 'Strandwanderung'),#
        ('trotzenburg', 'Trotzenburger Brauerei, 9 Euro'),#
        ('zoo', 'Zoo Rostock, max. 13,50 Euro'),#
       ]
    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)
    musikwunsch = StringField('Musikwunsch')
    #alternativprogramm = BooleanField('Ich habe Interesse an einem Alternativprogramm zur Kneipentour')

    anreise_verkehr = SelectField('Wie wäret ihr zur Ostsee-ZaPF gereist?', choices=[
        ('bus', 'Fernbus'),
        ('bahn', 'Zug'),
        ('auto', 'Auto'),
#        ('flug', 'Flugzeug'),
        ('zeitmaschine', 'Zeitmaschine'),
        ('boot', 'Boot'),
        ('fahrrad', 'Fahrrad'),
        ('badeente', 'Badeente'),
        ])
    tshirt = SelectField('T-Shirt', choices = T_SHIRT_CHOICES)
    addtshirt = IntegerField('Anzahl zusätzliche T-Shirts',[validators.optional()], widget=NumberInput())




    hoodie = SelectField('Ich möchte gerne einen Hoodie für max. XX Euro bestellen', choices = HOODIE_CHOICES)
    handtuch = BooleanField('Ich möchte gerne ein Handtuch für max. XX Euro bestellen')
    tasse = BooleanField('Ich möchte gerne eine Tasse für max. XX Euro bestellen')
    usb = BooleanField('Ich möchte gerne einen USB-Stick für max. XX Euro bestellen')
    frisbee = BooleanField('Ich möchte gerne eine Frisbee für max. XX Euro bestellen')
    aufnaeher = IntegerField('Anzahl Aufnäher',[validators.optional()], widget=NumberInput())
    schal = BooleanField('Ich möchte gerne einen Schlauchschal für max. XX Euro bestellen')



    bierak = BooleanField('Ich möchte am Bier-AK für maximal XX Euro teilnehmen.')
    zaepfchen = SelectField('Kommst du zum ersten mal zu einer ZaPF?', choices=[
        ('ja','Ja'),
        ('jaund','Ja und ich hätte gerne ein ZaPF-Mentikon.'),
        ('nein','Nein'),
        ])
    mentor = BooleanField('Ich möchte ZaPF-Mentikon werden und erkläre mich damit einverstanden, dass meine E-Mail-Adresse an ein Zäpfchen weitergegeben wird.')
    foto = BooleanField('Ich bin damit einverstanden, dass Fotos von mir gemacht werden.')
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
    schwimmabzeichen = SelectField('Welches Schwimmabzeichen hast du?', choices=[
        ('keins','keins'),
        ('bleiente','Bleiente'),
        ('seepferd','Seepferdchen'),
        ('bronze','Bronze'),
        ('silber','Silber'),
        ('gold','Gold'),
        ('rett','Rettungsschwimmer*in'),
    ])


@sommer21.route('/', methods=['GET', 'POST'])
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

    Form = Sommer21Registration

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

@sommer21.route('/admin/sose21/<string:username>', methods=['GET', 'POST'])
def adminEdit(username):
    if 'me' not in session:
        return redirect('/')

    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER
    if not is_admin:
        abort(403)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = Sommer21Registration

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
        return redirect(url_for('sommer21.adminEdit', username=username))

    return render_0emplate('index.html', form=form, confirmed=confirmed)


