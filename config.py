# """Flask config."""
# import os
# import redis

# class Config(object):

# class DevelopmentConfig(Config):

#     # General Config
#     FLASK_APP='wsgi.py'
#     SECRET_KEY='blahblahblahblah'
#     LOG_TO_STDOUT = os.environ('LOG_TO_STDOUT')

#     # Sessions
#     SESSION_TYPE=redis
#     SESSION_REDIS_URI='redis://h:p6bcf1416cf55cd74b9d1d5ac2f68241b1ad402c8972d15d5777ef4e85c53e1b7@ec2-3-226-133-138.compute-1.amazonaws.com:14919'
#     SESSION_COOKIE_NAME:'session'
#     # SESSION_COOKIE_SECURE=True
#     # SESSION_COOKIE_DOMAIN=None
#     # SESSION_COOKIE_HTTPONLY=True
#     # SESSION_COOKIE_PATH=None
#     # SESSION_COOKIE_SAMESITE=None 
#     # SESSION_COOKIE_SECURE=False
#     # SESSION_REFRESH_EACH_REQUEST=True 
#     # PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=31)

#     # ENV
#     DEBUG=True
#     ASSETS_DEBUG=True
#     COMPRESSOR_DEBUG=True
#     EXPLAIN_TEMPLATE_LOADING=True
     
#     # Flask-SQLAlchemy SQL Database
#     SQLALCHEMY_DATABASE_URI='postgres://zfgtcbuzkpjiod:b52325b1a9244f1d3cf8500d14ae165af1369d7eff7841f306746f6a4e0733f4@ec2-52-20-248-222.compute-1.amazonaws.com:5432/d37uou3e7j5m64'
#     # SQLALCHEMY_ECHO=True
#     # SQLALCHEMY_TRACK_MODIFICATIONS=False

#     # Static Assets
#     STATIC_FOLDER='static'
#     TEMPLATES_FOLDER='templates'
#     # APPLICATION_ROOT='/'
#     PALLETS='./CSV/pallets_dictionary.csv'
#     TEMP_IMG='static/temp.png'
    
#     # Cache
#     SEND_FILE_MAX_AGE_DEFAULT=1 # To ensure new image loads
#     # 'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(seconds=43200),
#     # TEMPLATES_AUTO_RELOAD=None

# class ProductionConfig(Config):
    
#     # General Config
#     FLASK_APP='wsgi.py'
#     SECRET_KEY=os.environ('SECRET_KEY')
#     LOG_TO_STDOUT = os.environ('LOG_TO_STDOUT')

#     # Sessions
#     SESSION_TYPE=redis
#     SESSION_REDIS_URI=os.environ('REDIS_URL')
#     SESSION_COOKIE_NAME:'session'
#     # SESSION_COOKIE_SECURE=True
#     # SESSION_COOKIE_DOMAIN=None
#     # SESSION_COOKIE_HTTPONLY=True
#     # SESSION_COOKIE_PATH=None
#     # SESSION_COOKIE_SAMESITE=None 
#     # SESSION_COOKIE_SECURE=False
#     # SESSION_REFRESH_EACH_REQUEST=True 
#     # PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=31)

#     # ENV
#     DEBUG=True
#     ASSETS_DEBUG=True
#     COMPRESSOR_DEBUG=True
#     EXPLAIN_TEMPLATE_LOADING=True
     
#     # Flask-SQLAlchemy SQL Database
#     SQLALCHEMY_DATABASE_URI=os.environ('HEROKU_POSTGRESQL_PURPLE_URL')
#     # SQLALCHEMY_ECHO=True
#     # SQLALCHEMY_TRACK_MODIFICATIONS=False

#     # Static Assets
#     STATIC_FOLDER='static'
#     TEMPLATES_FOLDER='templates'
#     # APPLICATION_ROOT='/'
#     PALLETS='./CSV/pallets_dictionary.csv'
#     TEMP_IMG='static/temp.png'
    
#     # Cache
#     SEND_FILE_MAX_AGE_DEFAULT=1 # To ensure new image loads
#     # 'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(seconds=43200),
#     # TEMPLATES_AUTO_RELOAD=None

# class TestingConfig(Config):
#     TESTING = True