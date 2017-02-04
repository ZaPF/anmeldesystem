from . import sommer17
from flask import render_template

@sommer17.route('/')
def index():
    return render_template('index.html')
