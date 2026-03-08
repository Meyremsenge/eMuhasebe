"""
eMuhasebe Pro - API Blueprint
REST API endpoint'leri — ORM + Repository + Service katmanlı mimarisi kullanır.
Frontend (Firebase) ile paralel çalışır; backend tarafında da tam CRUD desteği sağlar.
"""
from flask import Blueprint, jsonify, request
from app.services.musteri_service import MusteriService
from app.services.urun_service import UrunService
from app.services.fatura_service import FaturaService

api_bp = Blueprint('api', __name__)


# ══════════════════════ MÜŞTERİLER ══════════════════════

@api_bp.route('/musteriler', methods=['GET'])
def musteriler_list():
    """Tüm müşterileri listeler. ?q= ile arama destekler."""
    keyword = request.args.get('q', '').strip()
    if keyword:
        musteriler = MusteriService.search(keyword)
    else:
        musteriler = MusteriService.get_all()
    return jsonify([_musteri_to_dict(m) for m in musteriler])


@api_bp.route('/musteriler/<int:musteri_id>', methods=['GET'])
def musteriler_detail(musteri_id):
    """Tekil müşteri detayı."""
    musteri = MusteriService.get_by_id(musteri_id)
    if musteri is None:
        return jsonify({'error': 'Müşteri bulunamadı'}), 404
    return jsonify(_musteri_to_dict(musteri))


@api_bp.route('/musteriler', methods=['POST'])
def musteriler_create():
    """Yeni müşteri oluşturur."""
    data = request.get_json()
    if not data or not data.get('unvan'):
        return jsonify({'error': 'Ünvan zorunludur'}), 400
    try:
        musteri = MusteriService.create(data)
        return jsonify(_musteri_to_dict(musteri)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/musteriler/<int:musteri_id>', methods=['PUT'])
def musteriler_update(musteri_id):
    """Müşteriyi günceller."""
    data = request.get_json()
    try:
        musteri = MusteriService.update(musteri_id, data)
        return jsonify(_musteri_to_dict(musteri))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/musteriler/<int:musteri_id>', methods=['DELETE'])
def musteriler_delete(musteri_id):
    """Müşteriyi siler."""
    try:
        MusteriService.delete(musteri_id)
        return jsonify({'message': 'Müşteri silindi'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


# ══════════════════════ ÜRÜNLER ══════════════════════

@api_bp.route('/urunler', methods=['GET'])
def urunler_list():
    """Tüm ürünleri listeler. ?q= ile arama destekler."""
    keyword = request.args.get('q', '').strip()
    if keyword:
        urunler = UrunService.search(keyword)
    else:
        urunler = UrunService.get_all()
    return jsonify([_urun_to_dict(u) for u in urunler])


@api_bp.route('/urunler/<int:urun_id>', methods=['GET'])
def urunler_detail(urun_id):
    """Tekil ürün detayı."""
    urun = UrunService.get_by_id(urun_id)
    if urun is None:
        return jsonify({'error': 'Ürün bulunamadı'}), 404
    return jsonify(_urun_to_dict(urun))


@api_bp.route('/urunler', methods=['POST'])
def urunler_create():
    """Yeni ürün oluşturur."""
    data = request.get_json()
    if not data or not data.get('kod') or not data.get('ad'):
        return jsonify({'error': 'Kod ve ad zorunludur'}), 400
    try:
        urun = UrunService.create(data)
        return jsonify(_urun_to_dict(urun)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/urunler/<int:urun_id>', methods=['PUT'])
def urunler_update(urun_id):
    """Ürünü günceller."""
    data = request.get_json()
    try:
        urun = UrunService.update(urun_id, data)
        return jsonify(_urun_to_dict(urun))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/urunler/<int:urun_id>', methods=['DELETE'])
def urunler_delete(urun_id):
    """Ürünü siler."""
    try:
        UrunService.delete(urun_id)
        return jsonify({'message': 'Ürün silindi'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


# ══════════════════════ FATURALAR ══════════════════════

@api_bp.route('/faturalar/ozet', methods=['GET'])
def faturalar_summary():
    """Dashboard için fatura özet istatistikleri."""
    return jsonify(FaturaService.get_summary())


@api_bp.route('/faturalar/alis', methods=['GET'])
def alis_list():
    """Tüm alış faturalarını listeler."""
    faturalar = FaturaService.get_alis_all()
    return jsonify([_fatura_to_dict(f) for f in faturalar])


@api_bp.route('/faturalar/satis', methods=['GET'])
def satis_list():
    """Tüm satış faturalarını listeler."""
    faturalar = FaturaService.get_satis_all()
    return jsonify([_fatura_to_dict(f) for f in faturalar])


@api_bp.route('/faturalar/iade', methods=['GET'])
def iade_list():
    """Tüm iade faturalarını listeler."""
    faturalar = FaturaService.get_iade_all()
    return jsonify([_fatura_to_dict(f) for f in faturalar])


# ══════════════════════ HELPERS ══════════════════════

def _musteri_to_dict(m):
    return {
        'id': m.id,
        'unvan': m.unvan,
        'vergi_no': m.vergi_no,
        'vergi_dairesi': m.vergi_dairesi,
        'adres': m.adres,
        'telefon': m.telefon,
        'email': m.email,
        'tip': m.tip,
        'aktif': m.aktif,
    }


def _urun_to_dict(u):
    return {
        'id': u.id,
        'kod': u.kod,
        'ad': u.ad,
        'aciklama': u.aciklama,
        'birim': u.birim,
        'alis_fiyat': u.alis_fiyat,
        'satis_fiyat': u.satis_fiyat,
        'kdv_orani': u.kdv_orani,
        'stok_miktari': u.stok_miktari,
        'aktif': u.aktif,
    }


def _fatura_to_dict(f):
    return {
        'id': f.id,
        'fatura_no': f.fatura_no,
        'fatura_tarihi': str(f.fatura_tarihi) if f.fatura_tarihi else None,
        'ara_toplam': f.ara_toplam,
        'kdv_toplam': f.kdv_toplam,
        'genel_toplam': f.genel_toplam,
        'durum': f.durum,
        'aciklama': f.aciklama,
    }
