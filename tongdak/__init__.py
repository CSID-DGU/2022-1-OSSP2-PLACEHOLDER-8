import os
from cv2 import circle
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route('/position/<string:pair>')
    def test(pair):
        try:
            values = pair.split(';')
            x, y = float(values[0]), float(values[1])
            return str(x * y)
        except:
            return 'error'
    
    from . import circle_match
    app.register_blueprint(circle_match.bp)
    
    return app