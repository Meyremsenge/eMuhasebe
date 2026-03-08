import os

class Config:
    """Uygulama yapılandırma ayarları"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'muhasebe-gizli-anahtar-2024'
    
    # Veritabanı ayarları
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'instance', 'muhasebe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uygulama ayarları
    APP_NAME = 'eMuhasebe Pro'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 10
    
    # Para birimi
    CURRENCY = 'TL'
    CURRENCY_SYMBOL = '₺'


class DevelopmentConfig(Config):
    """Geliştirme ortamı ayarları"""
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class ProductionConfig(Config):
    """Üretim ortamı ayarları"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
