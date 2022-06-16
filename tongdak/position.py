import os

import click
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask.cli import with_appcontext
from scipy import interpolate
from werkzeug.utils import secure_filename

bp = Blueprint('position', __name__, url_prefix='/position')


# TODO: Delete after all work.
@bp.route('/', methods=('GET', 'POST'))
def test():
    return 'I am potato'


@click.command('init-heatmap')
@with_appcontext
def asdf():
    pass


"""
input: posx, posy
logic: call interpolation function
output: value
"""


@bp.route('/<string:map_id>/<string:coord>', methods=('GET', 'POST'))
def value(map_id: str, coord: str):
    try:
        values = list(map(float, coord.split(';')))
        return str(values)
    except:
        return "Invalid input: input url as 'float;float' format."


# update


# get snapshot


# TODO: upload heatmap
@bp.route('/functions', methods=('POST',))
def heatmap():
    if request.method == 'POST':
        try:
            f = request.files['file']
            
            f.save(os.path.join('instance', secure_filename(f.filename)))
            return 'file uploaded successfully'    
        except:
            return 'Fail'
    return 'Success'
