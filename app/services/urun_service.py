"""
Ürün Servisi - Ürün iş mantığı katmanı
"""
from app.repositories.urun_repository import UrunRepository


class UrunService:
    """Ürün iş kurallarını yöneten servis sınıfı."""

    @staticmethod
    def get_all():
        """Tüm ürünleri döndürür."""
        return UrunRepository.get_all()

    @staticmethod
    def get_by_id(urun_id):
        """ID'ye göre ürün getirir."""
        return UrunRepository.get_by_id(urun_id)

    @staticmethod
    def search(keyword):
        """Ürün adına göre arama yapar."""
        return UrunRepository.search_by_ad(keyword)

    @staticmethod
    def create(data):
        """Yeni ürün oluşturur. Kod benzersizlik kontrolü yapar."""
        if data.get('kod'):
            existing = UrunRepository.get_by_kod(data['kod'])
            if existing:
                raise ValueError('Bu ürün kodu zaten kayıtlı.')
        return UrunRepository.create(**data)

    @staticmethod
    def update(urun_id, data):
        """Ürünü günceller."""
        urun = UrunRepository.get_by_id(urun_id)
        if urun is None:
            raise ValueError('Ürün bulunamadı.')
        if data.get('kod') and data['kod'] != urun.kod:
            existing = UrunRepository.get_by_kod(data['kod'])
            if existing:
                raise ValueError('Bu ürün kodu başka bir ürüne ait.')
        return UrunRepository.update(urun_id, **data)

    @staticmethod
    def delete(urun_id):
        """Ürünü siler."""
        if not UrunRepository.exists(urun_id):
            raise ValueError('Ürün bulunamadı.')
        return UrunRepository.delete(urun_id)

    @staticmethod
    def get_aktif():
        """Aktif ürünleri döndürür."""
        return UrunRepository.get_aktif()

    @staticmethod
    def count():
        """Toplam ürün sayısını döndürür."""
        return UrunRepository.count()
