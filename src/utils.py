import dotenv
import os
import secrets

from flask.app import Flask
from flask import session
from sqlalchemy import create_engine

dotenv.load_dotenv()

def create_app():
    app = Flask(__name__,instance_relative_config=False)
    # Config: TODO: move into external dict.
    KEY = os.environ.get('SECRET_KEY')
    app.config['SECRET_KEY'] = KEY
    app.config['FLASK_APP'] = 'wsgi.py'
    app.config['DEBUG'] = True
    app.config['ASSETS_DEBUG'] = True
    app.config['COMPRESSOR_DEBUG'] = False
    app.config['STATIC_FOLDER'] = 'static'
    app.config['TEMPLATES_FOLDER'] = 'templates'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1 # To ensure new image loads
    return app

def create_db_connection():
    # SQL Connection
    HEROKU_POSTGRESQL = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL')
    return create_engine(HEROKU_POSTGRESQL)

def get_or_create_user_id():
    if session.get('user') is None:
        session['user'] = secrets.token_urlsafe(4)

def get_or_create_counter():
    if session.get('counter') is None:
        session['counter'] = 0
        
def create_cache_connection():
    return None
