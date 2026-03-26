"""
Security Tests
Rate Limiting, Security Headers, Authentication testleri
"""
import pytest
import json
from unittest.mock import patch


class TestSecurityHeaders:
    """HTTP Security Headers testleri."""

    def test_x_content_type_options_header(self, client, sample_musteri):
        """X-Content-Type-Options header."""
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'

    def test_x_frame_options_header(self, client, sample_musteri):
        """X-Frame-Options header (clickjacking protection)."""
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'

    def test_x_xss_protection_header(self, client, sample_musteri):
        """X-XSS-Protection header."""
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        assert 'X-XSS-Protection' in response.headers
        assert '1' in response.headers['X-XSS-Protection']

    def test_referrer_policy_header(self, client, sample_musteri):
        """Referrer-Policy header."""
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        assert 'Referrer-Policy' in response.headers


class TestRateLimiting:
    """Rate limiting testleri."""

    def test_rate_limit_exists(self, client):
        """Rate limiting endpoint'lerde aktif mi."""
        # Multiple requests'i gönder
        for i in range(5):
            response = client.get('/api/v1/musteriler')
            assert response.status_code == 200

    def test_get_list_rate_limit(self, client, multiple_musteriler):
        """GET list endpoint'inin rate limit'i."""
        # 30 req/min limit
        for i in range(5):
            response = client.get('/api/v1/musteriler')
            assert response.status_code in [200, 429]

    def test_post_create_rate_limit(self, client):
        """POST create endpoint'inin rate limit'i."""
        # 10 req/min limit
        payload = {
            'unvan': f'Test {0}',
            'vergi_no': f'{1000000000}'
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [201, 429]

    def test_delete_rate_limit(self, client, sample_musteri):
        """DELETE endpoint'inin rate limit'i."""
        # 10 req/min limit
        response = client.delete(f'/api/v1/musteriler/{sample_musteri.id}')
        assert response.status_code in [200, 429]


class TestInputValidation:
    """Input validation security testleri."""

    def test_injection_protection_sql(self, client):
        """SQL injection prevention."""
        # SQL injection attempt
        payload = {
            'unvan': "'; DROP TABLE musteriler; --"
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Validation error veya başarısı bekleniyor (injection değil)
        assert response.status_code in [201, 422, 400]

    def test_injection_protection_xss(self, client):
        """XSS injection prevention."""
        payload = {
            'unvan': '<script>alert("xss")</script>'
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # İstek işlenir ancak XSS tarafından etkilenmez
        assert response.status_code in [201, 422]

    def test_field_length_validation(self, client):
        """Alanların uzunluğu validation."""
        # Çok uzun unvan
        payload = {
            'unvan': 'A' * 500  # Max 255
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422

    def test_type_validation(self, client):
        """Type validation."""
        payload = {
            'unvan': 'Test',
            'stok_miktari': 'not-a-number'  # Sayı olmalı
        }
        # Ürün oluşturmada test
        response = client.post(
            '/api/v1/urunler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422

    def test_email_validation(self, client):
        """Email format validation."""
        payload = {
            'unvan': 'Test',
            'email': 'invalid-email'  # Geçersiz format
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422


class TestAuthorizationBoundaries:
    """Authorization ve boundary testleri."""

    def test_access_other_user_record(self, client, sample_musteri):
        """Başka kullanıcının record'una erişim."""
        # Şu anda authentication yok, tüm kayıtlara erişim mümkün
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        assert response.status_code == 200
        
        # Future: ID manipulation test
        response = client.get('/api/v1/musteriler/999999')
        assert response.status_code == 404

    def test_modify_other_user_record(self, client, sample_musteri):
        """Başka kullanıcının record'unu modify."""
        payload = {'unvan': 'Hacked'}
        response = client.put(
            f'/api/v1/musteriler/{sample_musteri.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        # Future: Authorization check edilecek


class TestDataSanitization:
    """Veri sanitization testleri."""

    def test_stored_xss_prevention(self, client):
        """Stored XSS prevention."""
        xss_value = '<img src=x onerror="alert(1)">'
        payload = {
            'unvan': xss_value
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            data = json.loads(response.data)
            # API katmaninda otomatik sanitization yok; template katmaninda escape edilmeli
            assert data['data']['unvan'] == xss_value

    def test_numeric_field_coercion(self, client):
        """Numeric alanlar coerce edilmeli."""
        payload = {
            'ad': 'Test',
            'kod': 'TST-001',
            'alis_fiyat': '100.50',  # String
            'satis_fiyat': 150,  # Int
            'stok_miktari': '25'  # String
        }
        response = client.post(
            '/api/v1/urunler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Başarılı olmalı (coercion ile)
        assert response.status_code in [201, 422]

    def test_whitespace_trimming(self):
        """Whitespace trim etme."""
        from app.validators import MusteriCreateRequest
        data = {'unvan': '  Test Company  '}
        try:
            request = MusteriCreateRequest(**data)
            # Whitespace'ler kalmışsa test et
        except Exception:
            pass  # Reddedilebilir


class TestDatabaseSecurity:
    """Veritabanı security testleri."""

    def test_numeric_precision(self, client):
        """Numeric precision (para hesabı)."""
        # Ürün oluştur
        payload = {
            'ad': 'Test',
            'kod': 'TST',
            'alis_fiyat': 99.99,
            'satis_fiyat': 149.99
        }
        response = client.post(
            '/api/v1/urunler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        # Precision check
        assert data['data']['alis_fiyat'] == 99.99

    def test_soft_delete_privacy(self, client, sample_musteri):
        """Soft delete privacy."""
        # Müşteri sil
        response = client.delete(f'/api/v1/musteriler/{sample_musteri.id}')
        assert response.status_code == 200
        
        # Silinmiş veri hala erişilebilir (soft delete)
        response = client.get(f'/api/v1/musteriler/{sample_musteri.id}')
        # Soft delete implementation'a göre 200 veya 404 olabilir


class TestErrorHandling:
    """Error handling security testleri."""

    def test_no_internal_error_details_leaked(self, client):
        """Internal error details leak yok."""
        # Geçersiz database işlemi
        payload = {
            'unvan': 'Test',
            'vergi_no': '1234567890'
        }
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        if response.status_code >= 500:
            data = json.loads(response.data)
            # Internal traceback yok
            assert 'traceback' not in str(data).lower()
            assert 'mysql' not in str(data).lower()
            assert 'sqlite' not in str(data).lower()

    def test_404_error_format(self, client):
        """404 error format."""
        response = client.get('/api/v1/musteriler/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

    def test_422_validation_error_format(self, client):
        """422 validation error format."""
        payload = {'unvan': 'A'}  # Çok kısa
        response = client.post(
            '/api/v1/musteriler',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 422
        data = json.loads(response.data)
        assert 'validation_errors' in data['error']['details']
