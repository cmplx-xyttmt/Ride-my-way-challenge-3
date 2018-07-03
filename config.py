from app.database_setup import config


class Config:
    """Parent configuration class"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = "this_is_the_secret_key"
    DATABASE_PARAMS = config()


class DevelopmentConfig(Config):
    """Configurations for Development"""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing, with a separate database."""
    TESTING = True
    DATABASE_PARAMS = config(section='testing')


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
