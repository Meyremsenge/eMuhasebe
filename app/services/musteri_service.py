"""
Müşteri Servisi - Müşteri iş mantığı katmanı
Route'lardan çağrılır; veri erişimi Repository üzerinden yapılır.
"""
from app.repositories.musteri_repository import MusteriRepository


class MusteriService:
    """Müşteri/Tedarikçi iş kurallarını yöneten servis sınıfı."""

    @staticmethod
    def get_all():
        """Tüm müşterileri döndürür."""
        return MusteriRepository.get_all()

    @staticmethod
    def get_by_id(musteri_id):
        """ID'ye göre müşteri getirir."""
        return MusteriRepository.get_by_id(musteri_id)

    @staticmethod
    def search(keyword):
        """Ünvana göre arama yapar."""
        return MusteriRepository.search_by_unvan(keyword)

    @staticmethod
    def create(data):
        """Yeni müşteri oluşturur. Vergi no kontrolü yapar."""
        if data.get('vergi_no'):
            existing = MusteriRepository.get_by_vergi_no(data['vergi_no'])
            if existing:
                raise ValueError('Bu vergi numarası zaten kayıtlı.')
        return MusteriRepository.create(**data)

    @staticmethod
    def update(musteri_id, data):
        """Müşteriyi günceller."""
        musteri = MusteriRepository.get_by_id(musteri_id)
        if musteri is None:
            raise ValueError('Müşteri bulunamadı.')
        if data.get('vergi_no') and data['vergi_no'] != musteri.vergi_no:
            existing = MusteriRepository.get_by_vergi_no(data['vergi_no'])
            if existing:
                raise ValueError('Bu vergi numarası başka bir müşteriye ait.')
        return MusteriRepository.update(musteri_id, **data)

    @staticmethod
    def delete(musteri_id):
        """Müşteriyi siler."""
        if not MusteriRepository.exists(musteri_id):
            raise ValueError('Müşteri bulunamadı.')
        return MusteriRepository.delete(musteri_id)

    @staticmethod
    def get_aktif():
        """Aktif müşterileri döndürür."""
        return MusteriRepository.get_aktif()

    @staticmethod
    def count():
        """Toplam müşteri sayısını döndürür."""
        return MusteriRepository.count()
