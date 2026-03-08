"""
Fatura Servisi - Fatura iş mantığı katmanı (alış, satış, iade)
"""
from app.repositories.alis_fatura_repository import AlisFaturaRepository
from app.repositories.satis_fatura_repository import SatisFaturaRepository
from app.repositories.iade_fatura_repository import IadeFaturaRepository


class FaturaService:
    """Fatura iş kurallarını yöneten servis sınıfı."""

    # ── Alış Faturaları ──

    @staticmethod
    def get_alis_all():
        return AlisFaturaRepository.get_all()

    @staticmethod
    def get_alis_by_id(fatura_id):
        return AlisFaturaRepository.get_by_id(fatura_id)

    @staticmethod
    def create_alis(fatura_data, kalemler_data):
        if AlisFaturaRepository.get_by_fatura_no(fatura_data.get('fatura_no')):
            raise ValueError('Bu fatura numarası zaten kayıtlı.')
        return AlisFaturaRepository.create_with_kalemler(fatura_data, kalemler_data)

    @staticmethod
    def delete_alis(fatura_id):
        if not AlisFaturaRepository.exists(fatura_id):
            raise ValueError('Alış faturası bulunamadı.')
        return AlisFaturaRepository.delete(fatura_id)

    # ── Satış Faturaları ──

    @staticmethod
    def get_satis_all():
        return SatisFaturaRepository.get_all()

    @staticmethod
    def get_satis_by_id(fatura_id):
        return SatisFaturaRepository.get_by_id(fatura_id)

    @staticmethod
    def create_satis(fatura_data, kalemler_data):
        if SatisFaturaRepository.get_by_fatura_no(fatura_data.get('fatura_no')):
            raise ValueError('Bu fatura numarası zaten kayıtlı.')
        return SatisFaturaRepository.create_with_kalemler(fatura_data, kalemler_data)

    @staticmethod
    def delete_satis(fatura_id):
        if not SatisFaturaRepository.exists(fatura_id):
            raise ValueError('Satış faturası bulunamadı.')
        return SatisFaturaRepository.delete(fatura_id)

    # ── İade Faturaları ──

    @staticmethod
    def get_iade_all():
        return IadeFaturaRepository.get_all()

    @staticmethod
    def get_iade_by_id(fatura_id):
        return IadeFaturaRepository.get_by_id(fatura_id)

    @staticmethod
    def create_iade(fatura_data, kalemler_data):
        if IadeFaturaRepository.get_by_fatura_no(fatura_data.get('fatura_no')):
            raise ValueError('Bu fatura numarası zaten kayıtlı.')
        return IadeFaturaRepository.create_with_kalemler(fatura_data, kalemler_data)

    @staticmethod
    def delete_iade(fatura_id):
        if not IadeFaturaRepository.exists(fatura_id):
            raise ValueError('İade faturası bulunamadı.')
        return IadeFaturaRepository.delete(fatura_id)

    # ── Özet İstatistikler ──

    @staticmethod
    def get_summary():
        """Dashboard için fatura özetleri."""
        return {
            'alis_count': AlisFaturaRepository.count(),
            'satis_count': SatisFaturaRepository.count(),
            'iade_count': IadeFaturaRepository.count(),
        }
