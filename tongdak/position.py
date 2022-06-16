import functools

import click
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask.cli import with_appcontext
from scipy import interpolate

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


@bp.route('/<string:values_str>', methods=('GET', 'POST'))
def value(values_str: str):
    try:
        values = list(map(float, values_str.split(';')))
        assert (values[0], float)
        assert (values[1], float)
        return str(values)
    except:
        return "Invalid input: input url as 'float;float' format."


# update


# get snapshot


# TODO: upload heatmap
@bp.route('/heatmap', methods=('POST', 'PUT'))
def heatmap():
    try:
        pass
    except:
        return 'Fail'
    return 'Success'
