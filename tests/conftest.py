"""
Test Yapılandırması - pytest fixture'ları
Her test in-memory SQLite veritabanı kullanır.
"""
import pytest
from app import create_app
from app.models import db as _db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'


@pytest.fixture
def app():
    """Test Flask uygulaması oluşturur."""
    app = create_app.__wrapped__ if hasattr(create_app, '__wrapped__') else create_app
    test_app = create_app('default')
    test_app.config.from_object(TestConfig)

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client'ı döndürür."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Veritabanı oturumunu döndürür."""
    with app.app_context():
        yield _db
