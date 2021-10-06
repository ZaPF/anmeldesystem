import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_COVERAGE = 0
    PREFERRED_URL_SCHEME = 'https'

    ZAPFAUTH_BASE_URL = 'https://auth.zapf.in/api/'
    ZAPFAUTH_AUTHORIZE_URL = 'https://auth.zapf.in/oauth/authorize'
    ZAPFAUTH_ACCESS_TOKEN_URL = 'https://auth.zapf.in/oauth/token'
    ZAPFAUTH_REQUEST_TOKEN_URL = None
    ZAPFAUTH_ACCESS_TOKEN_METHOD = 'POST'
    ZAPFAUTH_CONSUMER_KEY = 'a random string key'
    ZAPFAUTH_CONSUMER_SECRET = 'a random string secret'
    ZAPFAUTH_REVOKE_URL = 'https://auth.zapf.in/oauth/revoke'
    ZAPFAUTH_LOGOUT_URL = 'https://auth.zapf.in/logout'

    CURRENT_REGISTRATION = os.getenv('CURRENT_REGISTATION', 'sose2021')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    SECRET_KEY = 'secrets'
    PREFERRED_URL_SCHEME = 'http'
    ZAPFAUTH_BASE_URL = 'http://test.auth.zapf.in/api/'
    ZAPFAUTH_AUTHORIZE_URL = 'http://test.auth.zapf.in/oauth/authorize'
    ZAPFAUTH_ACCESS_TOKEN_URL = 'http://test.auth.zapf.in/oauth/token'
    DEBUG=True

    @staticmethod
    def init_app(app):
        print("Development config")
        import os
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

