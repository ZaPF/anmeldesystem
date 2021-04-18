
# coding=utf-8
from . import winter20
from flask import render_template, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, validators, IntegerField, RadioField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.widgets.html5 import NumberInput
from app.oauth_client import oauth_remoteapp, getOAuthToken
import json
from datetime import datetime, time, timezone, timedelta
import pytz

REGISTRATION_SOFT_CLOSE = datetime(2020, 10, 3, 21, 59, 59, tzinfo=pytz.utc)
REGISTRATION_HARD_CLOSE = datetime(2020, 10, 4, 21, 59, 59, tzinfo=pytz.utc)
ADMIN_USER = ['t.prinz']

T_SHIRT_CHOICES = [
        ('keins', 'Nein, ich möchte kein T-Shirt'),
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
        ('keins', 'Nein, ich möchte keine Sweatjacke'),
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
                                                     '"Keine Exkursion" stehen, alles andere ist '
                                                     'nicht sinnvoll ;).')
        elif field.data != "egal":
            for follower in self.following:
                if follower.data == field.data:
                    raise validators.ValidationError('Selbe Exkursion mehrfach als Wunsch ausgewählt')

class Winter20Registration(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(Winter20Registration, self).__init__(**kwargs)
        self.exkursion1.validators=[ExkursionenValidator([self.exkursion2, self.exkursion3, self.exkursion4])]
        self.exkursion2.validators=[ExkursionenValidator([self.exkursion3, self.exkursion4])]
        self.exkursion3.validators=[ExkursionenValidator([self.exkursion4])]
        self.immatrikuliert.validators=[ImmatrikulationsValidator(self.immatrikuliert)]
        self.immatrikulationsbescheinigung.validators=[ImmatrikulationsValidator2(self.immatrikulationsbescheinigung)]
    
    adresse = TextAreaField('Adresse*')
    telefon = StringField('Telefonnummer*', default='+49 ')

    uni = SelectField('Uni*', [validators.InputRequired()], choices=[], coerce=str)
    spitzname = StringField('Spitzname/Rufname')
    immatrikuliert = RadioField('Bringst du deine Immatrikulationsbescheinigung mit?*', choices=[
            ('ja', 'Ich bin an einer Hochschule immatrikuliert und bringe eine gültige Bescheinigung darüber mit.'),
            ('nein', 'Ich bin an einer Hochschule immatrikuliert und bringe keine gültige Bescheinigung darüber mit.'),	
            ('n.i.', 'Ich bin an keiner Hochschule immatrikuliert und bringe keine gültige Bescheinigung darüber mit.'),
            ])
    immatrikulationsbescheinigung = RadioField('Wirst du deine Immatrikulationsbescheinigung vergessen?*', choices=[
            ('ja', 'Ja.'),
            ('nein', 'Nein.'),
            ('n.i.', 'Ich habe keine.'),
    ]) 
    essen = SelectField('Essen', choices=[
        ('omnivor', 'Omnivor'),
        ('vegetarisch', 'Vegetarisch'),
        ('vegan', 'Vegan'),
        ])
    allergien = StringField('Hast du irgendwelche Allergien oder andere Essenseinschränkungen?')
    alkohol = BooleanField('Ich trinke Alkohol')
#'''    heissgetraenk = SelectField('Kaffee oder Tee?', choices=[
#        ('egal', 'Egal'),
#        ('kaffee', 'Kaffee'),
#        ('tee', 'Tee'),
#        ])'''
#   essenswunsch = StringField('Unverbindlicher Essenswunsch:')
#
    exkursionen = [
        ('keine', 'keine Exkursion'),#
        ('egal', 'Ist mir egal'),#
        ('eso', 'ESO - Europäische Südsternwarte'),#
        ('ipp', 'IPP - Max-Plank-Institut für Plasmaphysik'),#
        ('mpq', 'MPQ - Max-Plank-Institut für Quantenoptik'),#
        ('mpe', 'MPE - Max-Plank-Institut für Extraterrestrische Physik'),#
        ('mpa', 'MPA - Max-Plank-Institut für Astrophysik'),#
        ('lrz', 'LRZ - Leibniz-Rechenzentrum'),#
        ('frm2', 'FRM II'),#
        ('stadtfuehrung', 'Stadtführung Garching'),#
        ('isarwanderung', 'Isarwanderung'),#
        ('campusfuehrung', 'Ausgiebigerere Campusführung'),#
        ('lss', 'Führung durch das LSS'),#
        ('aisec', 'Fraunhofer AISEC'),
       ]
    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)
    musikwunsch = StringField('Musikwunsch')
    #alternativprogramm = BooleanField('Ich habe Interesse an einem Alternativprogramm zur Kneipentour')

    anreise_verkehr = SelectField('Wie kommst du zu uns?', choices=[
        ('', ' --- '),
        ('bus', 'Fernbus'),
        ('bahn', 'Zug'),
        ('auto', 'Auto'),
        ('flug', 'Flugzeug'),
#       ('zeitmaschine', 'Zeitmaschine'),
        ('floss', 'Floß'),
        ('fahrrad', 'Fahrrad'),
        ('sonstige', 'Sonstige'),
    ])
# '''   anreise_zeit = SelectField('Anreise vorraussichtlich:', choices=[
#        ('mi1416', 'Mittwoch 14-16 Uhr'),
#        ('mi1618', 'Mittwoch 16-18 Uhr'),
#        ('mi1820', 'Mittwoch 18-20 Uhr'),
#        ('mi2022', 'Mittwoch 20-22 Uhr'),
#        ('ende', 'Später'),
#        ])'''

#    excar = BooleanField('Ich reise mit einem Auto an und bin bereit, auf Exkursionen Zapfika mitzunehmen.')

    abreise_zeit = SelectField('Abreise vorraussichtlich:', choices=[
        ('', ' --- '),
        ('fr', 'Freitag'),
        ('sa', 'Samstag'),
        ('sovormittag', 'Sonntag Vormittag'),
        ('soabend', 'Sonntag Abend'),
        ('monacht', 'Nacht auf Montag'),
        ('movormittag', 'Montag Vormittag'),
        ])

    eigene_unterkunft = BooleanField('Ich könnte mich selber um eine Unterkunft kümmern, falls ihr mir keinen Schlafplatz anbieten könnt.')

#   schlafen = SelectField('Unterkunft', choices=[
#       ('egal','Egal'),
#       ('MZH','Unterkunft A'),
#       ('FW','Unterkunft B'),
#       ])
    tshirt = SelectField('T-Shirt', choices = T_SHIRT_CHOICES)
    addtshirt = IntegerField('Anzahl zusätzliche T-Shirts',[validators.optional()], widget=NumberInput())




    hoodie = SelectField('Ich möchte gerne eine Sweatjacke für 25 Euro bestellen.', choices = HOODIE_CHOICES)
    krug = BooleanField('Ich möchte gerne einen Maßkrug für 15 Euro bestellen.')
    muetze = BooleanField('Ich möchte gerne eine Mütze für 10 Euro bestellen.')


#    bierak = BooleanField('Ich möchte am Bier-AK für maximal 10 Euro teilnehmen.')
    zaepfchen = SelectField('Kommst du zum ersten mal zu einer ZaPF?*', [validators.InputRequired()], choices=[
        ('','Bitte auswählen'),
        ('jamentor','Ja und ich hätte gerne einen ZaPF-Mentor.'),
        ('ja','Ja, aber ich möchte keinen Mentor oder bringe meinen eigenen Mentor mit.'),
        ('nein','Nein'),
        ])
    mentor = BooleanField('Ich möchte ZaPF-Mentor werden und erkläre mich damit einverstanden, dass meine E-Mail-Adresse an ein Zäpfchen weitergegeben wird.')
#    foto = BooleanField('Ich bin damit einverstanden, dass Fotos von mir gemacht werden.')
#    halle = BooleanField('Ich habe die Hallenordnung (siehe <a href="https://bonn.zapf.in/index.php/hallenordnung/">Website</a>) gelesen und verstanden und werde mich daran halten.', [validators.InputRequired()])
    minderjaehrig = BooleanField('Ich bin zum Zeitpunkt der ZaPF JÜNGER als 18 Jahre.')
    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',
#   gremien = BoolanField('Ich bin Mitglied in StAPF, TOPF, KommGrem, oder ZaPF-e.V-Vorstand und moechte mich über das Gremienkontingent anmelden.')
    widget = TextArea())
    submit = SubmitField()




    anrede= SelectField('Wie möchtest du angesprochen werden?',choices=[
            ('ka',''),
            ('er','Er/Ihm'),
            ('sie','Sie/Ihr'),
            ('es','Es/Ihm'),
            ('siemehrzahl','Sie (Mehrzahl)/Ihnen'),
            ('vorname','Mit meinem Vornamen/Spitznamen'),
            ('anderes','Sprich mich darauf an'),
            ], default="")
    vertrauensperson = BooleanField('Ich möchte mich als Vertrauensperson zur Wahl stellen.')
    stream = RadioField('Wärst du damit einverstanden, dass die Plenen Live ins Internet gestreamt werden?*', [validators.InputRequired()], choices=[
        ('nein', 'Nein'),
        ('japasswort', 'Ja, wenn nur Fachschaftika zugänglich (Passwortgeschützt)'),
        ('ja', 'Ja, auch öffentlich'),
        ])
    protokoll = BooleanField('Ich wäre bereit, bei den Plenen Protokoll zu schreiben.')
    langzeithelfikon = BooleanField('Ich bin bereit, im laufe der ZaPF mehr als 12 Stunden als Helfikon tätig zu sein.')
# '''   schwimmabzeichen = SelectField('Welches Schwimmabzeichen hast du?', choices=[
#        ('keins','keins'),
#        ('seepferd','Seepferdchen'),
#        ('bronze','Bronze'),
#        ('silber','Silber'),
#        ('gold','Gold'),
#        ('rett','Rettungsschwimmer*in'),
#    ])'''
    datenschutz = BooleanField('Ich habe die Datenschutzerklärung gelesen und bin mit der darin beschriebenen Verarbeitung meiner Daten einverstanden.*', [validators.InputRequired()])
    corona = BooleanField('Ich bin mir bewusst, dass vor der Tagung eine Hausordnung inklusive Hygienemaßnahmen veröffentlicht wird und werde mich an diese Regeln halten.', [validators.InputRequired()])
    korrekt = BooleanField('Die oben angegebenen Daten sind meine eigenen, korrekt und aktuell. Sollten sie sich bis zum Ende der ZaPF ändern, werde ich die ausrichtende Fachschaft darüber informieren.', [validators.InputRequired()])


@winter20.route('/', methods=['GET', 'POST'])
def index():
    registration_open = datetime.now(pytz.utc) <= REGISTRATION_SOFT_CLOSE
    priorities_open   = datetime.now(pytz.utc) <= REGISTRATION_HARD_CLOSE
    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER

    if not is_admin and not priorities_open:
        return render_template('registration_closed.html')

    if 'me' not in session:
        return render_template('landing.html', registration_open = registration_open, priorities_open = priorities_open, registration_close=(REGISTRATION_SOFT_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z"), REGISTRATION_HARD_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z")))

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = Winter20Registration

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
    form.uni.choices = [('','Bitte Auswählen')] + sorted(unis.data.items(), key=lambda uniEntry: int(uniEntry[0]))

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

    return render_template('index.html', form=form, confirmed=confirmed, registration_close=(REGISTRATION_SOFT_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z"), REGISTRATION_HARD_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z")))

@winter20.route('/admin/wise20/<string:username>', methods=['GET', 'POST'])
def adminEdit(username):
    if 'me' not in session:
        return redirect('/')

    is_admin = 'me' in session and session['me']['username'] in ADMIN_USER
    if not is_admin:
        abort(403)

    if not getOAuthToken():
        flash("Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.", 'warning')
        return redirect(url_for('oauth_client.login'))

    Form = Winter20Registration

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
    form.uni.choices = sorted(unis.data.items())

    # Daten speichern
    if form.submit.data and form.validate_on_submit():
        req = oauth_remoteapp.post('registration', format='json', data=dict(username = username,
            uni_id = form.uni.data, data={k:v for k,v in form.data.items() if k not in ['csrf_token', 'submit']}
            ))
        if req._resp.code == 200 and req.data.decode('utf-8') == "OK":
            flash('Deine Anmeldedaten wurden erfolgreich gespeichert', 'info')
        else:
            flash('Deine Anmeldendaten konnten nicht gespeichert werden.', 'error')
        return redirect(url_for('winter20.adminEdit', username=username))

    return render_template('index.html', form=form, confirmed=confirmed, registration_close=(REGISTRATION_SOFT_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z"), REGISTRATION_HARD_CLOSE.astimezone(pytz.timezone("Europe/Berlin")).strftime("%d.%m. um %H:%M Uhr %Z")))


