"""
eMuhasebe Pro - Veritabanı Modelleri
Tüm veritabanı tablolarının tanımları
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Musteri(db.Model):
    """Müşteri/Tedarikçi bilgileri"""
    __tablename__ = 'musteriler'
    
    id = db.Column(db.Integer, primary_key=True)
    unvan = db.Column(db.String(200), nullable=False)
    vergi_no = db.Column(db.String(11), unique=True)
    vergi_dairesi = db.Column(db.String(100))
    adres = db.Column(db.Text)
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(120))
    tip = db.Column(db.String(20), default='musteri')  # musteri, tedarikci, her_ikisi
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    alis_faturalari = db.relationship('AlisFatura', backref='tedarikci', lazy='dynamic')
    satis_faturalari = db.relationship('SatisFatura', backref='musteri', lazy='dynamic')
    iade_faturalari = db.relationship('IadeFatura', backref='firma', lazy='dynamic')
    
    def __repr__(self):
        return f'<Musteri {self.unvan}>'


class Urun(db.Model):
    """Ürün/Hizmet tanımları"""
    __tablename__ = 'urunler'
    
    id = db.Column(db.Integer, primary_key=True)
    kod = db.Column(db.String(50), unique=True, nullable=False)
    ad = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    birim = db.Column(db.String(20), default='Adet')
    alis_fiyat = db.Column(db.Float, default=0)
    satis_fiyat = db.Column(db.Float, default=0)
    kdv_orani = db.Column(db.Integer, default=20)
    stok_miktari = db.Column(db.Float, default=0)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Urun {self.kod} - {self.ad}>'


class AlisFatura(db.Model):
    """Alış faturaları"""
    __tablename__ = 'alis_faturalari'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_no = db.Column(db.String(50), unique=True, nullable=False)
    fatura_tarihi = db.Column(db.Date, nullable=False)
    vade_tarihi = db.Column(db.Date)
    tedarikci_id = db.Column(db.Integer, db.ForeignKey('musteriler.id'), nullable=False)
    
    # Tutar bilgileri
    ara_toplam = db.Column(db.Float, default=0)
    kdv_toplam = db.Column(db.Float, default=0)
    indirim_toplam = db.Column(db.Float, default=0)
    genel_toplam = db.Column(db.Float, default=0)
    
    # Durum bilgileri
    durum = db.Column(db.String(20), default='beklemede')  # beklemede, odendi, iptal
    aciklama = db.Column(db.Text)
    
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kalemler = db.relationship('AlisFaturaKalem', backref='fatura', lazy='dynamic', cascade='all, delete-orphan')
    
    def hesapla(self):
        """Fatura toplamlarını hesapla"""
        self.ara_toplam = sum(k.toplam for k in self.kalemler)
        self.kdv_toplam = sum(k.kdv_tutar for k in self.kalemler)
        self.genel_toplam = self.ara_toplam + self.kdv_toplam - self.indirim_toplam
    
    def __repr__(self):
        return f'<AlisFatura {self.fatura_no}>'


class AlisFaturaKalem(db.Model):
    """Alış fatura kalemleri"""
    __tablename__ = 'alis_fatura_kalemleri'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_id = db.Column(db.Integer, db.ForeignKey('alis_faturalari.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'))
    
    aciklama = db.Column(db.String(300))
    miktar = db.Column(db.Float, default=1)
    birim = db.Column(db.String(20), default='Adet')
    birim_fiyat = db.Column(db.Float, default=0)
    kdv_orani = db.Column(db.Integer, default=20)
    indirim_orani = db.Column(db.Float, default=0)
    
    @property
    def toplam(self):
        """Kalem toplamı (KDV hariç)"""
        tutar = self.miktar * self.birim_fiyat
        indirim = tutar * (self.indirim_orani / 100)
        return tutar - indirim
    
    @property
    def kdv_tutar(self):
        """KDV tutarı"""
        return self.toplam * (self.kdv_orani / 100)
    
    @property
    def genel_toplam(self):
        """KDV dahil toplam"""
        return self.toplam + self.kdv_tutar


class SatisFatura(db.Model):
    """Satış faturaları"""
    __tablename__ = 'satis_faturalari'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_no = db.Column(db.String(50), unique=True, nullable=False)
    fatura_tarihi = db.Column(db.Date, nullable=False)
    vade_tarihi = db.Column(db.Date)
    musteri_id = db.Column(db.Integer, db.ForeignKey('musteriler.id'), nullable=False)
    
    # Tutar bilgileri
    ara_toplam = db.Column(db.Float, default=0)
    kdv_toplam = db.Column(db.Float, default=0)
    indirim_toplam = db.Column(db.Float, default=0)
    genel_toplam = db.Column(db.Float, default=0)
    
    # Durum bilgileri
    durum = db.Column(db.String(20), default='beklemede')  # beklemede, tahsil_edildi, iptal
    aciklama = db.Column(db.Text)
    
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kalemler = db.relationship('SatisFaturaKalem', backref='fatura', lazy='dynamic', cascade='all, delete-orphan')
    
    def hesapla(self):
        """Fatura toplamlarını hesapla"""
        self.ara_toplam = sum(k.toplam for k in self.kalemler)
        self.kdv_toplam = sum(k.kdv_tutar for k in self.kalemler)
        self.genel_toplam = self.ara_toplam + self.kdv_toplam - self.indirim_toplam
    
    def __repr__(self):
        return f'<SatisFatura {self.fatura_no}>'


class SatisFaturaKalem(db.Model):
    """Satış fatura kalemleri"""
    __tablename__ = 'satis_fatura_kalemleri'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_id = db.Column(db.Integer, db.ForeignKey('satis_faturalari.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'))
    
    aciklama = db.Column(db.String(300))
    miktar = db.Column(db.Float, default=1)
    birim = db.Column(db.String(20), default='Adet')
    birim_fiyat = db.Column(db.Float, default=0)
    kdv_orani = db.Column(db.Integer, default=20)
    indirim_orani = db.Column(db.Float, default=0)
    
    @property
    def toplam(self):
        """Kalem toplamı (KDV hariç)"""
        tutar = self.miktar * self.birim_fiyat
        indirim = tutar * (self.indirim_orani / 100)
        return tutar - indirim
    
    @property
    def kdv_tutar(self):
        """KDV tutarı"""
        return self.toplam * (self.kdv_orani / 100)
    
    @property
    def genel_toplam(self):
        """KDV dahil toplam"""
        return self.toplam + self.kdv_tutar


class IadeFatura(db.Model):
    """İade faturaları"""
    __tablename__ = 'iade_faturalari'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_no = db.Column(db.String(50), unique=True, nullable=False)
    fatura_tarihi = db.Column(db.Date, nullable=False)
    firma_id = db.Column(db.Integer, db.ForeignKey('musteriler.id'), nullable=False)
    
    # İade türü
    iade_turu = db.Column(db.String(20), nullable=False)  # alis_iade, satis_iade
    referans_fatura_no = db.Column(db.String(50))  # İlişkili orijinal fatura
    
    # Tutar bilgileri
    ara_toplam = db.Column(db.Float, default=0)
    kdv_toplam = db.Column(db.Float, default=0)
    genel_toplam = db.Column(db.Float, default=0)
    
    # Durum bilgileri
    durum = db.Column(db.String(20), default='beklemede')  # beklemede, tamamlandi, iptal
    iade_nedeni = db.Column(db.Text)
    aciklama = db.Column(db.Text)
    
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    kalemler = db.relationship('IadeFaturaKalem', backref='fatura', lazy='dynamic', cascade='all, delete-orphan')
    
    def hesapla(self):
        """Fatura toplamlarını hesapla"""
        self.ara_toplam = sum(k.toplam for k in self.kalemler)
        self.kdv_toplam = sum(k.kdv_tutar for k in self.kalemler)
        self.genel_toplam = self.ara_toplam + self.kdv_toplam
    
    def __repr__(self):
        return f'<IadeFatura {self.fatura_no}>'


class IadeFaturaKalem(db.Model):
    """İade fatura kalemleri"""
    __tablename__ = 'iade_fatura_kalemleri'
    
    id = db.Column(db.Integer, primary_key=True)
    fatura_id = db.Column(db.Integer, db.ForeignKey('iade_faturalari.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'))
    
    aciklama = db.Column(db.String(300))
    miktar = db.Column(db.Float, default=1)
    birim = db.Column(db.String(20), default='Adet')
    birim_fiyat = db.Column(db.Float, default=0)
    kdv_orani = db.Column(db.Integer, default=20)
    
    @property
    def toplam(self):
        """Kalem toplamı (KDV hariç)"""
        return self.miktar * self.birim_fiyat
    
    @property
    def kdv_tutar(self):
        """KDV tutarı"""
        return self.toplam * (self.kdv_orani / 100)
    
    @property
    def genel_toplam(self):
        """KDV dahil toplam"""
        return self.toplam + self.kdv_tutar
