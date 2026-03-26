import os
import secrets

class Config:
    """Uygulama yapılandırma ayarları"""
    
    # ━━━ SECRET_KEY Güvenliği ━━━
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Üretimde hata, geliştirmede random oluştur
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError(
                '❌ CRITICAL: SECRET_KEY ortam değişkeni set edilmemiş!\n'
                'Üretim ortamında SECRET_KEY zorunludur.\n'
                '.env dosyasını kontrol edin: SECRET_KEY=<32-char-key>'
            )
        # Geliştirmede random oluştur (her restart'ta değişir ama sorun değil)
        SECRET_KEY = secrets.token_hex(32)
    
    # ━━━ Veritabanı Ayarları ━━━
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'instance', 'muhasebe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ━━━ Session Güvenliği ━━━
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True  # JavaScript erişimini engelle
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF koruması
    PERMANENT_SESSION_LIFETIME = 86400  # 24 saat
    
    # ━━━ Uygulama Ayarları ━━━
    APP_NAME = 'eMuhasebe Pro'
    APP_VERSION = '1.0.0'
    ITEMS_PER_PAGE = 10
    
    # ━━━ Para Birimi ━━━
    CURRENCY = 'TL'
    CURRENCY_SYMBOL = '₺'


class DevelopmentConfig(Config):
    """Geliştirme ortamı ayarları"""
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    TESTING = False


class ProductionConfig(Config):
    """Üretim ortamı ayarları"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    
    # Üretimde zorunlu validasyonlar
    def __init__(self):
        """Üretim başlangıcında güvenlik kontrolleri"""
        super().__init__()
        
        # DATABASE_URL kontrol et
        if not os.environ.get('DATABASE_URL'):
            raise ValueError(
                '❌ CRITICAL: DATABASE_URL ortam değişkeni set edilmemiş!\n'
                'Üretim ortamında DATABASE_URL zorunludur.'
            )
        
        print('✅ Production config: Tüm güvenlik kontrolleri geçildi')


class TestingConfig(Config):
    """Test ortamı ayarları"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key-for-testing-only'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
