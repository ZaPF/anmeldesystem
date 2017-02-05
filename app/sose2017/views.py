from . import sommer17
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField
from wtforms.ext.dateutil.fields import DateField
from wtforms.widgets import TextArea

class Sommer17Registration(FlaskForm):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

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
        ('awi', 'Alfred-Wegener-Institut für Polar- und Meeresforschung'),
        ('spektrum', 'Technik-Museum und Science Center Spektrum (mit Option auf Naturkundemuseum)'),
        ('fub', 'Uni-Tour: Freie Universität Berlin'),
        ('tub', 'Uni-Tour: Technische Universität Berlin'),
        ('golm', 'Uni-Tour: Uni Golm (+ neues Palais)'),
        ('stad', 'Klassische Stadtführung mit Reichstagsbesichtigung'),
        ('hipster', 'Alternative Hipster-Stadtführung mit Streetart'),
        ('unterwelten', 'Berliner Unterwelten'),
        ('potsdam', 'Schlösser und Gärten Tour Potsdam'),
        ]

    exkursion1 = SelectField('Erstwunsch', choices=exkursionen)
    exkursion2 = SelectField('Zweitwunsch', choices=exkursionen)
    exkursion3 = SelectField('Drittwunsch', choices=exkursionen)
    exkursion4 = SelectField('Viertwunsch', choices=exkursionen)

    geburtsdatum = DateField('Geburtsdatum', display_format='%d.%m.%Y')

    alkoholfrei = BooleanField('Ich möchte statt an einer Kneipentour lieber an '
                               'einem alkoholfreien Alternativprogramm in Berlin '
                               'teilnehmen')
    musikwunsch = StringField('Musikwunsch')

    kommentar = StringField('Möchtest Du uns sonst etwas mitteilen?',
            widget = TextArea())

    submit = SubmitField()

@sommer17.route('/')
def index():
    Form = Sommer17Registration

    # Zwischen 6:00 und 7:00
    from datetime import datetime, time
    now = datetime.now().time()
    if time(6,00) <= now <= time(7,00):
        Form = Form.append_field('wach', StringField('Warum bist Du grade wach?',
                widget = TextArea()))

    form = Form()
    return render_template('index.html', form=form)
