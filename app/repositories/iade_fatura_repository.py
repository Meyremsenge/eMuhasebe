"""
İade Fatura Repository - İade faturası verisi erişim katmanı
"""
from app.models import IadeFatura, IadeFaturaKalem, db
from app.repositories.base_repository import BaseRepository


class IadeFaturaRepository(BaseRepository):
    """İade faturası tablosuna yönelik veri erişim metotları."""

    model = IadeFatura

    @classmethod
    def get_by_fatura_no(cls, fatura_no):
        """Fatura numarasına göre tekil kayıt getirir."""
        return IadeFatura.query.filter_by(fatura_no=fatura_no).first()

    @classmethod
    def get_by_firma(cls, firma_id):
        """Firmaya ait iade faturalarını döndürür."""
        return cls.filter_by(firma_id=firma_id)

    @classmethod
    def get_by_iade_turu(cls, iade_turu):
        """İade türüne göre filtreler (alis_iade, satis_iade)."""
        return cls.filter_by(iade_turu=iade_turu)

    @classmethod
    def create_with_kalemler(cls, fatura_data, kalemler_data):
        """Fatura ve kalemlerini birlikte oluşturur."""
        fatura = IadeFatura(**fatura_data)
        db.session.add(fatura)
        db.session.flush()

        for kalem_data in kalemler_data:
            kalem_data['fatura_id'] = fatura.id
            kalem = IadeFaturaKalem(**kalem_data)
            db.session.add(kalem)

        fatura.hesapla()
        db.session.commit()
        return fatura
