import os
from flask import Flask, request, jsonify, make_response
from . import init

def create_app(config=os.environ['APP_SETTINGS']):
    app = Flask(__name__)
    app.config.from_object(config)
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    init(app)
    from .route import app as route_app
    app.register_blueprint(route_app)
    return app


if  __name__ == '__main__':  
    app = create_app()
    app.run(debug=True)
