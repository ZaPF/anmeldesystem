# coding=utf-8
from . import reg_blueprint
from flask import render_template, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    BooleanField,
    validators,
    IntegerField,
)
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.widgets.html5 import NumberInput
from app.oauth_client import oauth_remoteapp, getOAuthToken
import json
from datetime import datetime, time, timezone
import pytz


## Merch Auswahloptionen definieren

T_SHIRT_CHOICES = [
    ("keins", "Nein, ich möchte keins"),
    ("xxl", "XXL"),
    ("xl", "XL"),
    ("l", "L"),
    ("m", "M"),
    ("s", "S"),
    ("xs", "XS"),
]

# Gerne auskommentierte Sachen wieder reinnehmen, falls ihr motivierter wart mit der Merchbeschaffung als wir

# HOODIE_CHOICES = [
#        ('keins', 'Nein, ich möchte keinen'),
#        ('fitted_xxl', 'XXL fitted'),
#       ('fitted_xl', 'XL fitted'),
#       ('fitted_l', 'L fitted'),
#        ('fitted_m', 'M fitted'),
#        ('fitted_s', 'S fitted'),
#        ('fitted_xs', 'XS fitted'),
#        ('5xl', '5XL'),
#        ('4xl', '4XL'),
#        ('3xl', '3XL'),
#        ('xxl', 'XXL'),
#        ('xl', 'XL'),
#        ('l', 'L'),
#        ('m', 'M'),
#        ('s', 'S'),
#        ('xs', 'XS'),
#        ]


# MERCH_COLORS = [
#        ('navy','Navy'),
#        ('grau','Dunkelgrau'),
#        ('schwarz','Schwarz'),
#        ]


class ImmatrikulationsValidator(object):
    def __init__(self, following=None):
        self.following = following

    def __call__(self, form, field):
        if field.data != "ja" and field.data != "n.i.":
            raise validators.ValidationError(
                "Bitte gib an, dass du deine Immatrikulationsbescheinigung mitbringen wirst oder, dass du keine hast."
            )


class ImmatrikulationsValidator2(object):
    def __init__(self, following=None):
        self.following = following

    def __call__(self, form, field):
        if field.data != "nein" and field.data != "n.i.":
            raise validators.ValidationError(
                "Bitte gib an, dass du deine Immatrikulationsbescheinigung nicht vergessen wirst."
            )


class ExkursionenValidator(object):
    def __init__(self, following=None):
        self.following = following

    def __call__(self, form, field):
        if field.data == "keine":
            for follower in self.following:
                if follower.data != "keine":
                    raise validators.ValidationError(
                        "Die folgenden Exkursionen sollten auch auf "
                        '"Keine Exkursion" stehen, alles anderes ist '
                        "nicht sinnvoll ;)."
                    )
        elif field.data != "egal":
            for follower in self.following:
                if follower.data == field.data:
                    raise validators.ValidationError(
                        "Selbe Exkursion mehrfach als Wunsch ausgewählt"
                    )


class RegistrationForm(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

    def __init__(self, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.immatrikulationsbescheinigung.validators = [
            ImmatrikulationsValidator(self.immatrikulationsbescheinigung)
        ]
        self.immatrikulationsbescheinigung2.validators = [
            ImmatrikulationsValidator2(self.immatrikulationsbescheinigung2)
        ]

    #### Allgemein #####
    uni = SelectField("Uni", choices=[], coerce=str)
    spitzname = StringField("Spitzname")
    # Die Abfrage, ob Immabescheinigung mitgebracht wird geschieht später an zwei Orten. Einmal im allgemeinen Teil und die erinnerung am Ende der Anmeldung
    immatrikulationsbescheinigung = SelectField(
        "Bringst du deine Immatrikulationsbescheinigung mit?",
        choices=[
            ("invalid", "---"),
            (
                "ja",
                "Ich bin an einer Hochschule immatrikuliert und bringe eine gültige Bescheinigung darüber mit.",
            ),
            (
                "nein",
                "Ich bin an einer Hochschule immatrikuliert und bringe keine gültige Bescheinigung darüber mit.",
            ),
            (
                "n.i.",
                "Ich bin an keiner Hochschule immatrikuliert und bringe keine gültige Bescheinigung darüber mit.",
            ),
        ],
    )
    immatrikulationsbescheinigung2 = SelectField(
        "Wirst du deine Immatrikulationsbescheinigung vergessen?",
        choices=[
            ("invalid", "---"),
            ("ja", "Ja."),
            ("nein", "Nein."),
            ("n.i.", "Ich habe keine."),
        ],
    )
    anrede = SelectField(
        "Wie möchtest du angesprochen werden?",
        choices=[
            ("ka", "Keine Angabe"),
            ("er", "Er"),
            ("sie", "Sie"),
            ("anderes", "Sprich mich darauf an"),
            ("aendern", "Ich möchte die Möglichkeit haben, diese Angabe während der Tagung zu ändern"),
            ("sonstiges", "Nichts davon, ich möchte das Freitextfeld nutzen."),
        ],
    )
    anrede2 = StringField("Ich möchte angesprochen werden mit:")

    musikwunsch = StringField("Musikwunsch")

    ###### Essen ######

    essen = SelectField(
        "Essen",
        choices=[
            ("omnivor", "Omnivor"),
            ("vegetarisch", "Vegetarisch"),
            ("vegan", "Vegan"),
        ],
    )
    essensmenge = SelectField(
        "Wieviele Brötchen würdest du morgens essen",
        choices=[
	    ("weniger", "Weniger!"),
            ("eins", "Eins"),
            ("zwei", "Zwei"),
            ("drei", "Drei"),
            ("mehr", "Mehr!"),
        ],
    )
    allergien = StringField("Allergien")
    essensformen = StringField("Sonstige Essensformen z.B. koscher") 
    heissgetraenk = SelectField(
        "Kaffee oder Tee?",
        choices=[
            #        ('egal', 'Egal'),
            ("kaffee", "Kaffee"),
            ("tee", "Tee"),
            ("unparteiisch", "Unparteiisches Alpaka"),
        ],
    )
    alkohol = SelectField(
        "Trinkst du Alkohol",
        choices=[
            ("ja", "Ja"),
            ("nein", "Nein"),
            ("ka", "Keine Angabe"),
        ],
    )

    ##### Rahmenprogramm ####

    exkursionen = [
        ("egal", "Ist mir egal (es werden noch weiter Exkursionen angekündigt)"),
        ("spaziergang", "Spaziergang um den Kemnader See mit Besuch im Botanischen Garten"),
        ("planetarium", "Planetariumvorstellung (Faszinierendes Weltall) mit anschließender Erklärung der Technik"),
        ("lehrstuhlvorstellung", "Lehrstuhlvorstellung"),
        ("bergbaumuseum", "Bergbaumuseum"),
        ("keine", "Keine Exkursion"),
    ]
    exkursion1 = SelectField("Erstwunsch", choices=exkursionen)
    exkursion2 = SelectField("Zweitwunsch", choices=exkursionen)
    exkursion3 = SelectField("Drittwunsch", choices=exkursionen)
    exkursion4 = SelectField("Viertwunsch", choices=exkursionen)

    bierak = BooleanField(
        "Ich möchte am Bieraustausch AK teilnehmen."
    )

    # alternativprogramm = BooleanField('Ich habe Interesse an einem Alternativprogramm zur Kneipentour')

    #### Merch #####

    tshirt = SelectField("T-Shirt", choices=T_SHIRT_CHOICES)
    nrtshirt = IntegerField(
        "Anzahl T-Shirts", [validators.optional()], widget=NumberInput(min=0, max=10)
    )
    tasse = BooleanField(
         "Ich möchte eine Tagungstasse haben (ca 5€)."
    )
    nottasche = BooleanField(
         "Ich möchte keine Tagungstasche haben (den Inhalt kriegst du trotzdem)."
    )
    

    #### Reiseinfos ####

    anreise_witz = SelectField(
        "Verkehrsmittel deiner Wahl",
        choices=[
            ("bus", "Fernbus"),
            ("bahn", "Zug"),
            ("auto", "Auto"),
            ("zeitmaschine", "Zeitmaschine"),
            ("flohpulver", "Flohpulver"),
            ("fahrrad", "Fahrrad"),
            ("badeente", "Badeente"),
        ],
    )
    anreise_zeit = SelectField(
        "Anreise vorraussichtlich:",
        choices=[
            ("frueher", "Ich komme früher und helfe gerne beim Aufbau."),
            ("fr1214", "Freitag 12-14 Uhr"),
            ("fr1416", "Freitag 14-16 Uhr"),
            ("fr1618", "Freitag 16-18 Uhr"),
            ("fr1820", "Freitag 18-20 Uhr"),
            ("ende", "Später"),
        ],
    )

    #   excar = BooleanField('Ich reise mit einem Auto an und bin bereit, auf Exkursionen Zapfika mitzunehmen.')

    abreise_zeit = SelectField(
        "Abreise vorraussichtlich:",
        choices=[
            ("vordi", "Vor Dienstag"),
            ("di810", "Dienstag 8-10 Uhr"),
            ("di1012", "Dienstag 10-12 Uhr"),
            ("di1214", "Dienstag 12-14 Uhr"),
            ("di1416", "Dienstag 14-16 Uhr"),
            ("di1618", "Dienstag 16-18 Uhr"),
            ("di1820", "Dienstag 18-20 Uhr"),
            ("ende", "Nach dem Plenum"),
        ],
    )

    ##### Standorte ######
    modus = SelectField(
        "Ich möchte in folgendem Modus an der Tagung teilnehmen:",
        choices=[
            ("online", "Online-Teilnahme"),
            ("present", "Präsenzteilnahme"),
        ],
    )

    barrierefreiheit = BooleanField(
        "Ich habe spezifische Ansprüche an Barrierefreiheit."
    )

    eduroam = BooleanField(
        "Ich habe Eduroam (Internet-Zugangsdienst)."
    )
    
    nrwticket = SelectField(
        "Ich habe ein NRW-Ticket.",
        choices=[
            ("nein", "Nein"),
            ("ja", "Ja"),
            ("jaund", "Ja und ich kann in Bochum jemanden darauf mitnehmen."),
        ],
    )

    impfstatus = SelectField(
        "Impfstatus",
        choices=[
            ("keinfach", "ungeimpft"),
            ("geimpft", "geimpft"),
            ("geboostert", "geimft und geboostert"),
            ("genesen", "genesen"),
            ("genimpft", "geimpft und genesen, bzw geimpft, geboostert und genesen"),
            ("impfbefreiung", "kann mich aus medizinischen Gründen nicht impfen lassen"),
            ("kA", "keine Angabe"),
        ],
    )

    impfzertifikat = BooleanField(
        "Ich werde meinen (digitalen) Impfausweis, ein Zertifikat über meine Genesung oder einen Nachweis über die Befreiung von der 2G Pflicht dabei haben und bei Bedarf vorzeigen"
    )

    coronatest = BooleanField(
        "Ich lasse mich testen, sodass ich jeden Tag einen gültigen Test vorweisen kann."
    )



    notbinarytoiletten = BooleanField(
                "Ich möchte während der ZaPF die Möglichkeit haben nicht binär-geschlechtliche Toiletten zu verwenden"
            )
    notbinaryduschen = BooleanField(
                "Ich möchte während der ZaPF die Möglichkeit haben nicht binär-geschlechtliche Duschen zu verwenden"
            )
    notgruppenduschen = BooleanField(
                "Ich möchte keine Gruppendusche nutzen müssen."
            )
    nurohnegruppenduschen = BooleanField(
                "Wenn ich eine Gruppendusche nutzen muss, würde ich lieber gar nicht in Präsenz kommen"
            )
        
    

    foerderung = BooleanField("Ja")

    hygiene = BooleanField("Ja")

    #### Sonstiges ####
    zaepfchen = SelectField(
        "Kommst du zum ersten mal zu einer ZaPF?",
        choices=[
            ("ja", "Ja"),
            ("jaund", "Ja und ich hätte gerne einen ZaPF-Mentor."),
            ("nein", "Nein"),
        ],
    )
    mentor = BooleanField(
        "Ich möchte ZaPF-Mentorikon werden und erkläre mich damit einverstanden, dass meine E-Mail-Adresse an ein Zäpfchen weitergegeben wird."
    )
    foto = BooleanField(
        "Ich bin damit einverstanden, dass Fotos von mir gemacht werden. Diese werden evtl im Tagungsreader genutzt. und nicht für kommerzielle Zwecke verwendet."
    )
    alter = SelectField(
        "Ich bin zum Zeitpunkt der ZaPF:",
        choices=[
            ("u16", "JÜNGER als 16 Jahre"),
            ("u18", "JÜNGER als 18 Jahre"),
            ("18-26", "ZWISCHEN 18 und 26 Jahren"),
            ("a26", "ÄLTER als 26 Jahre"),
        ],
    )
    kommentar = StringField(
        "Möchtest Du uns sonst etwas mitteilen?",
        #   gremien = BoolanField('Ich bin Mitglied in StAPF, TOPF, KommGrem, oder ZaPF-e.V-Vorstand und moechte mich über das Gremienkontingent anmelden.')
        widget=TextArea(),
    )
    submit = SubmitField()
    vertrauensperson = SelectField(
        'Wärst Du bereit, dich als Vertrauensperson aufzustellen? (Du weißt nicht was das ist? Gib bitte "Nein" an!)',
        choices=[
            ("nein", "Nein"),
            ("ja", "Ja"),
        ],
    )
    protokoll = SelectField(
        "Wärst Du bereit bei den Plenen Protokoll zu schreiben?",
        choices=[
            ("nein", "Nein"),
            ("ja", "Ja"),
        ],
    )
    ##### Datenschutz ######

    datenschutz = BooleanField("Ja", [validators.InputRequired()])


@reg_blueprint.route("/", methods=["GET", "POST"])
def index():
    registration_open = (
        datetime.now(pytz.utc) <= current_app.config["REGISTRATION_SOFT_CLOSE"]
    ) or current_app.config["REGISTRATION_FORCE_OPEN"]
    priorities_open = (
        datetime.now(pytz.utc) <= current_app.config["REGISTRATION_HARD_CLOSE"]
    ) or current_app.config["REGISTRATION_FORCE_PRIORITIES_OPEN"]
    is_admin = (
        "me" in session
        and session["me"]["username"] in current_app.config["ADMIN_USERS"]
    )

    if not is_admin and not priorities_open:
        return render_template("registration_closed.html")

    if "me" not in session:
        return render_template(
            "landing.html",
            registration_open=registration_open,
            priorities_open=priorities_open,
        )

    if not getOAuthToken():
        flash(
            "Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.",
            "warning",
        )
        return redirect(url_for("oauth_client.login"))

    Form = RegistrationForm

    defaults = {}
    confirmed = None
    req = oauth_remoteapp.get("registration")
    if req._resp.code == 200:
        defaults = json.loads(req.data["data"])
        if "geburtsdatum" in defaults and defaults["geburtsdatum"]:
            defaults["geburtsdatum"] = datetime.strptime(
                defaults["geburtsdatum"], "%Y-%m-%d"
            )
        confirmed = req.data["confirmed"]
    else:
        if not is_admin and not registration_open:
            return render_template("registration_closed.html")

    # Formular erstellen
    form = Form(**defaults)

    # Die Liste der Unis holen
    unis = oauth_remoteapp.get("unis")
    if unis._resp.code == 500:
        raise
    if unis._resp.code != 200:
        return redirect(url_for("oauth_client.login"))
    form.uni.choices = sorted(unis.data.items(), key=lambda uniEntry: int(uniEntry[0]))

    # Daten speichern
    if form.submit.data and form.validate_on_submit():
        req = oauth_remoteapp.post(
            "registration",
            format="json",
            data=dict(
                uni_id=form.uni.data,
                data={
                    k: v
                    for k, v in form.data.items()
                    if k not in ["csrf_token", "submit"]
                },
            ),
        )
        if req._resp.code == 200 and req.data.decode("utf-8") == "OK":
            flash("Deine Anmeldedaten wurden erfolgreich gespeichert", "info")
        else:
            flash("Deine Anmeldendaten konnten nicht gespeichert werden.", "error")
        return redirect("/")

    return render_template("index.html", form=form, confirmed=confirmed)


@reg_blueprint.route("/admin/wise21/<string:username>", methods=["GET", "POST"])
def adminEdit(username):
    if "me" not in session:
        return redirect("/")

    is_admin = (
        "me" in session
        and session["me"]["username"] in current_app.config["ADMIN_USERS"]
    )
    if not is_admin:
        abort(403)

    if not getOAuthToken():
        flash(
            "Die Sitzung war abgelaufen, eventuell musst du deine Daten nochmal eingeben, falls sie noch nicht gespeichert waren.",
            "warning",
        )
        return redirect(url_for("oauth_client.login"))

    Form = RegistrationForm

    defaults = {}
    confirmed = None
    req = oauth_remoteapp.get("registration", data={"username": username})
    if req._resp.code == 200:
        defaults = json.loads(req.data["data"])
        if "geburtsdatum" in defaults and defaults["geburtsdatum"]:
            defaults["geburtsdatum"] = datetime.strptime(
                defaults["geburtsdatum"], "%Y-%m-%d"
            )
        confirmed = req.data["confirmed"]
    elif req._resp.code == 409:
        flash("Username is unknown", "error")
        return redirect("/")

    # Formular erstellen
    form = Form(**defaults)

    # Die Liste der Unis holen
    unis = oauth_remoteapp.get("unis")
    if unis._resp.code != 200:
        return redirect(url_for("oauth_client.login"))
    form.uni.choices = sorted(unis.data.items(), key=lambda uniEntry: int(uniEntry[0]))

    # Daten speichern
    if form.submit.data and form.validate_on_submit():
        req = oauth_remoteapp.post(
            "registration",
            format="json",
            data=dict(
                username=username,
                uni_id=form.uni.data,
                data={
                    k: v
                    for k, v in form.data.items()
                    if k not in ["csrf_token", "submit"]
                },
            ),
        )
        if req._resp.code == 200 and req.data.decode("utf-8") == "OK":
            flash("Deine Anmeldedaten wurden erfolgreich gespeichert", "info")
        else:
            flash("Deine Anmeldendaten konnten nicht gespeichert werden.", "error")
        return redirect(url_for("sommer20.adminEdit", username=username))

    return render_template("index.html", form=form, confirmed=confirmed)
