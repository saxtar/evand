import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    S3_KEY = os.environ['S3_KEY']
    S3_SECRET = os.environ['S3_SECRET']
    S3_BUCKET = os.environ['S3_BUCKET']
    S3_EP = os.environ['S3_EP']
    PURCHASE_API_KEY = os.environ['PURCHASE_API_KEY']
    HOST_URL = os.environ['HOST_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://sammy:password@localhost:5432"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://sammy:password@localhost:5432/test"
