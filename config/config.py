class Config:
    DEBUG = False
    CSRF_ENABLED = True


class Development(Config):
    DEBUG = True
    red_flags = {}


class Testing(Config):
    DEBUG = True
    TESTING = True
    red_flags = {}


class Production(Config):
    DEBUG = False
    TESTING = False

app_config = {
    'DEVELOPMENT': Development, 'TESTING': Testing, 'PRODUCTION': Production
    }
