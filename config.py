import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_COVERAGE = 0
    PREFERRED_URL_SCHEME = 'https'

    ZAPFAUTH_CONSUMER_KEY = 'a random string key'
    ZAPFAUTH_CONSUMER_SECRET = 'a random string secret'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SECRET_KEY = 'secrets'
    DEBUG=True

class ProductionConfig(Config):
    LOGPATH='logs'

class TestingConfig(Config):
    DEBUG=True
    TESTING=True
    FLASK_COVERAGE = 1
    SECRET_KEY = 'secrets'
    WTF_CSRF_ENABLED = False


config = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig
        }

