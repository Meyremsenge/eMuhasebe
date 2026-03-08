"""
Satış Fatura Repository - Satış faturası verisi erişim katmanı
"""
from app.models import SatisFatura, SatisFaturaKalem, db
from app.repositories.base_repository import BaseRepository


class SatisFaturaRepository(BaseRepository):
    """Satış faturası tablosuna yönelik veri erişim metotları."""

    model = SatisFatura

    @classmethod
    def get_by_fatura_no(cls, fatura_no):
        """Fatura numarasına göre tekil kayıt getirir."""
        return SatisFatura.query.filter_by(fatura_no=fatura_no).first()

    @classmethod
    def get_by_musteri(cls, musteri_id):
        """Müşteriye ait faturaları döndürür."""
        return cls.filter_by(musteri_id=musteri_id)

    @classmethod
    def get_by_durum(cls, durum):
        """Duruma göre filtreler (beklemede, odendi, iptal)."""
        return cls.filter_by(durum=durum)

    @classmethod
    def create_with_kalemler(cls, fatura_data, kalemler_data):
        """Fatura ve kalemlerini birlikte oluşturur."""
        fatura = SatisFatura(**fatura_data)
        db.session.add(fatura)
        db.session.flush()

        for kalem_data in kalemler_data:
            kalem_data['fatura_id'] = fatura.id
            kalem = SatisFaturaKalem(**kalem_data)
            db.session.add(kalem)

        fatura.hesapla()
        db.session.commit()
        return fatura
