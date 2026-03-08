@echo off
title eMuhasebe Pro - Baslatiyor...
color 0A

echo.
echo  ============================================
echo       eMuhasebe Pro v1.0.0
echo       On Muhasebe Yonetim Sistemi
echo  ============================================
echo.
echo  Uygulama baslatiliyor...
echo.

:: Python yolunu kontrol et
set PYTHON_PATH=C:\Users\TuncayErol\AppData\Local\Programs\Python\Python313\python.exe

if not exist "%PYTHON_PATH%" (
    echo  [HATA] Python bulunamadi!
    echo  Lutfen Python'u yukleyin.
    pause
    exit /b 1
)

:: Uygulama dizinine git
cd /d "%~dp0"

:: 2 saniye bekle ve tarayiciyi ac
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Flask uygulamasini baslat
echo  Sunucu baslatiliyor: http://127.0.0.1:5000
echo.
echo  Kapatmak icin bu pencereyi kapatin veya Ctrl+C basin.
echo  ============================================
echo.

"%PYTHON_PATH%" run.py
