"""
Temel Repository sınıfı - Tüm repository'ler bu sınıftan türer.
CRUD, filtreleme, listeleme ve arama gibi ortak veri erişim metotlarını sağlar.
"""
from app.models import db


class BaseRepository:
    """Genel CRUD ve sorgulama metotlarını barındıran temel repository."""

    model = None  # Alt sınıflar tarafından atanır

    @classmethod
    def get_by_id(cls, record_id):
        """ID'ye göre tekil kayıt getirir."""
        return cls.model.query.get(record_id)

    @classmethod
    def get_all(cls):
        """Tüm kayıtları döndürür."""
        return cls.model.query.all()

    @classmethod
    def filter_by(cls, **kwargs):
        """Verilen kriterlere göre filtreler."""
        return cls.model.query.filter_by(**kwargs).all()

    @classmethod
    def search(cls, column, keyword):
        """Belirli bir sütunda LIKE araması yapar."""
        return cls.model.query.filter(column.ilike(f'%{keyword}%')).all()

    @classmethod
    def create(cls, **kwargs):
        """Yeni kayıt oluşturur ve döndürür."""
        instance = cls.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    @classmethod
    def update(cls, record_id, **kwargs):
        """Mevcut kaydı günceller."""
        instance = cls.get_by_id(record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance

    @classmethod
    def delete(cls, record_id):
        """Kaydı siler. Başarılıysa True döndürür."""
        instance = cls.get_by_id(record_id)
        if instance is None:
            return False
        db.session.delete(instance)
        db.session.commit()
        return True

    @classmethod
    def count(cls):
        """Toplam kayıt sayısını döndürür."""
        return cls.model.query.count()

    @classmethod
    def paginate(cls, page=1, per_page=10):
        """Sayfalama ile kayıtları döndürür."""
        return cls.model.query.paginate(page=page, per_page=per_page, error_out=False)

    @classmethod
    def exists(cls, record_id):
        """Kayıt var mı kontrol eder."""
        return cls.get_by_id(record_id) is not None
