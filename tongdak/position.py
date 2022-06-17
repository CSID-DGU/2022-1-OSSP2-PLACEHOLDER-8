import pickle
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

def load_collection():
    with open(os.path.join('instance', secure_filename('obj.pickle')), 'rb') as pickle_file:
        kd_func_collection = pickle.load(pickle_file)
        g.collection = kd_func_collection
        print(g.collection)
    return g.collection

@bp.route('/<string:map_id>/<string:coord>', methods=('GET', 'POST'))
def value(map_id: str, coord: str):
    try:
        values = list(map(float, coord.split(';')))
        print(values[0], values[1])
        collection = getattr(g, 'collection', None)
        print(collection)
        if collection is None:
            collection = load_collection()
        print(collection)
        print(collection[map_id](values[0], values[1]))
        return str(collection[map_id](values[0], values[1]))
    except Exception as e:
        print(e)
        return "Invalid input: input url as 'float;float' format."


@bp.route('/functions', methods=('POST',))
def heatmap():
    if request.method == 'POST':
        try:
            f = request.files['file']
            print(f, 'Uploaded!')
            f.save(os.path.join('tongdak', 'instance', secure_filename('instance.pickle')))
        except:
            return 'Fail'
    
    with open(os.path.join('tongdak', 'instance', secure_filename('instance.pickle')), 'rb') as pickle_file:
        kd_func_collection = pickle.load(pickle_file)
        g.collection = kd_func_collection
        print(g.collection)

    return 'Success'
