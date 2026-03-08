"""
eMuhasebe Pro - Uygulama Başlatıcı
"""
import webbrowser
import threading
import sys
import os
from app import create_app

app = create_app('development')

def open_browser():
    """Uygulama başladıktan sonra tarayıcıyı aç"""
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  eMuhasebe Pro v1.0.0")
    print("  Ön Muhasebe Yönetim Sistemi")
    print("="*50)
    print("\n  Uygulama başlatılıyor...")
    print("  http://127.0.0.1:5000 adresinde çalışıyor")
    print("  Kapatmak için bu pencereyi kapatın.\n")
    
    # Tarayıcıyı 1.5 saniye sonra aç (sunucu başlayana kadar bekle)
    threading.Timer(1.5, open_browser).start()
    
    # Production modunda çalıştır (debug=False)
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
