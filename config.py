class Config:
    """Parent configuration class"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = "this_is_the_secret_key"


class DevelopmentConfig(Config):
    """Configurations for Development"""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing, with a separate database."""
    TESTING = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
