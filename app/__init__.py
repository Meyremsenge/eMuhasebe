"""
eMuhasebe Pro - Flask Uygulama Fabrikası (Factory Pattern)
Katmanlı Mimari: Route → Service → Repository → ORM
"""
from flask import Flask
from flask_migrate import Migrate
from config import config
from app.models import db

migrate = Migrate()


def create_app(config_name='default'):
    """Flask uygulama fabrikası"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Veritabanı ve migration başlat
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Blueprint'leri kaydet
    from app.main import main_bp
    from app.faturalar.alis import alis_bp
    from app.faturalar.satis import satis_bp
    from app.faturalar.iade import iade_bp
    from app.musteriler import musteriler_bp
    from app.urunler import urunler_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(alis_bp, url_prefix='/faturalar/alis')
    app.register_blueprint(satis_bp, url_prefix='/faturalar/satis')
    app.register_blueprint(iade_bp, url_prefix='/faturalar/iade')
    app.register_blueprint(musteriler_bp, url_prefix='/musteriler')
    app.register_blueprint(urunler_bp, url_prefix='/urunler')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Veritabanı tablolarını migration ile oluştur
    # db.create_all() kullanılmaz, flask db upgrade komutu ile yönetilir
    
    return app
