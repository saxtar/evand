import os
from flask import Flask
from . import init
from dotenv import load_dotenv, find_dotenv

def create_app(config=None):
    load_dotenv(find_dotenv())
    app = Flask(__name__)
    if config is None:
        config = os.environ['APP_SETTINGS']
    app.config.from_object(config)
    init(app)
    os.system('alembic upgrade head')
    from .user_routes import app as user_routes_app
    from .ticket_routes import app as ticket_routes_app
    from .event_routes import app as event_routes_app
    app.register_blueprint(user_routes_app)
    app.register_blueprint(ticket_routes_app)
    app.register_blueprint(event_routes_app)
    return app

