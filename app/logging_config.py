"""
Logging Configuration Module
Uygulamanın tüm logging ihtiyaçlarını merkezi olarak yönetir.
- Console logging (development)
- File logging with rotation (production)
- SQL query logging (SQLAlchemy DEBUG)
- API request/response logging (middleware)
- Error/exception tracking
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logging(app):
    """
    Flask uygulaması için logging'i yapılandırır.
    
    Args:
        app: Flask application instance
    
    Environment Variables:
        FLASK_ENV: development|production (default: development)
        LOG_LEVEL: DEBUG|INFO|WARNING|ERROR|CRITICAL (default: INFO)
        LOG_DIR: Log dosyalarının dizini (default: ./logs)
    """
    
    # Log dizini oluştur
    log_dir = Path(os.environ.get('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    # Log seviyesi ayarla
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Root logger'ı yapılandır
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Mevcut handler'ları temizle (multiple initialization'den kaçın)
    root_logger.handlers.clear()
    
    # Formatter - detaylı format
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler (her zaman ekrana yazı)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler - RotatingFileHandler (production)
    main_log_file = log_dir / 'app.log'
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(main_log_file),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,  # 10 backup file
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Erro-specific File Handler
    error_log_file = log_dir / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        filename=str(error_log_file),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # SQL Query Logging (SQLAlchemy)
    if os.environ.get('FLASK_ENV') == 'development':
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Flask internal logger
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Adlandırılmış logger döndürür. Tüm modüllerde kullan:
    
    Example:
        logger = get_logger(__name__)
        logger.info("User login: %s", username)
        logger.error("Database error occurred", exc_info=True)
    """
    return logging.getLogger(name)


# Audit Log Helper Functions
def log_audit_action(logger, user_id, action, tablo_adi, kayit_id, eski_veriler=None, yeni_veriler=None):
    """
    Muhasebe işlemlerini audit trail olarak kaydetir.
    
    Args:
        logger: Logger instance
        user_id: İşlemi yapan kullanıcı ID'si
        action: CREATE|UPDATE|DELETE
        tablo_adi: Tablo adı (e.g., musteriler, urunler)
        kayit_id: Kayıt ID'si
        eski_veriler: Eski değerler (UPDATE/DELETE için)
        yeni_veriler: Yeni değerler (CREATE/UPDATE için)
    
    Example:
        log_audit_action(
            logger, 
            user_id=1, 
            action='UPDATE', 
            tablo_adi='musteriler',
            kayit_id=5,
            eski_veriler={'unvan': 'ABC Ltd'},
            yeni_veriler={'unvan': 'ABC Inc'}
        )
    """
    message = f"AUDIT: [{action}] {tablo_adi} (ID: {kayit_id}) by user {user_id}"
    if eski_veriler or yeni_veriler:
        message += f" | Old: {eski_veriler} | New: {yeni_veriler}"
    logger.info(message)


def log_api_call(logger, method, endpoint, user_id=None, ip_address=None, response_code=None, duration_ms=None):
    """
    API çağrılarını kaydeder.
    
    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (/api/musteriler, etc.)
        user_id: İsteği yapan kullanıcı ID'si
        ip_address: İstemci IP adresi
        response_code: HTTP response kodu
        duration_ms: İsteğin süresi (milisaniye)
    
    Example:
        log_api_call(
            logger,
            method='POST',
            endpoint='/api/musteriler',
            user_id=1,
            ip_address='192.168.1.1',
            response_code=201,
            duration_ms=245
        )
    """
    log_parts = [f"API: {method} {endpoint}"]
    if user_id:
        log_parts.append(f"user={user_id}")
    if ip_address:
        log_parts.append(f"ip={ip_address}")
    if response_code:
        log_parts.append(f"status={response_code}")
    if duration_ms:
        log_parts.append(f"duration={duration_ms}ms")
    
    logger.info(" | ".join(log_parts))


def log_error_context(logger, error_type, error_msg, context=None):
    """
    Hatalar için context bilgisi ile log kaydı oluşturur.
    
    Args:
        logger: Logger instance
        error_type: Hata sınıfı adı
        error_msg: Hata mesajı
        context: İlgili context bilgisi (dict)
    
    Example:
        log_error_context(
            logger,
            error_type='DatabaseError',
            error_msg='Connection failed',
            context={'host': 'localhost', 'port': 5432}
        )
    """
    context_str = " | ".join([f"{k}={v}" for k, v in context.items()]) if context else ""
    message = f"ERROR [{error_type}]: {error_msg}"
    if context_str:
        message += f" | {context_str}"
    logger.error(message, exc_info=True)
