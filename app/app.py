import os
from flask import Flask
from . import init
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS, cross_origin


def create_app(config=None):
    load_dotenv(find_dotenv())
    app = Flask(__name__)
    if config is None:
        config = os.environ['APP_SETTINGS']
    app.config.from_object(config)
    init(app)
    cors = CORS(app)
    
    os.system('alembic upgrade head')
    from .user_routes import app as user_routes_app
    from .ticket_routes import app as ticket_routes_app
    from .event_routes import app as event_routes_app
    from .purchase_routes import app as purchase_routes_app
    from .category_routes import app as category_routes_app
    from .file_routes import app as file_routes_app
    app.register_blueprint(user_routes_app)
    app.register_blueprint(ticket_routes_app)
    app.register_blueprint(event_routes_app)
    app.register_blueprint(category_routes_app)
    app.register_blueprint(purchase_routes_app)
    app.register_blueprint(file_routes_app)
    return app

