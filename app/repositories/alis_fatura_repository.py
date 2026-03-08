"""
Alış Fatura Repository - Alış faturası verisi erişim katmanı
"""
from app.models import AlisFatura, AlisFaturaKalem, db
from app.repositories.base_repository import BaseRepository


class AlisFaturaRepository(BaseRepository):
    """Alış faturası tablosuna yönelik veri erişim metotları."""

    model = AlisFatura

    @classmethod
    def get_by_fatura_no(cls, fatura_no):
        """Fatura numarasına göre tekil kayıt getirir."""
        return AlisFatura.query.filter_by(fatura_no=fatura_no).first()

    @classmethod
    def get_by_tedarikci(cls, tedarikci_id):
        """Tedarikçiye ait faturaları döndürür."""
        return cls.filter_by(tedarikci_id=tedarikci_id)

    @classmethod
    def get_by_durum(cls, durum):
        """Duruma göre filtreler (beklemede, odendi, iptal)."""
        return cls.filter_by(durum=durum)

    @classmethod
    def create_with_kalemler(cls, fatura_data, kalemler_data):
        """Fatura ve kalemlerini birlikte oluşturur."""
        fatura = AlisFatura(**fatura_data)
        db.session.add(fatura)
        db.session.flush()  # ID atanması için

        for kalem_data in kalemler_data:
            kalem_data['fatura_id'] = fatura.id
            kalem = AlisFaturaKalem(**kalem_data)
            db.session.add(kalem)

        fatura.hesapla()
        db.session.commit()
        return fatura
