# API v1 Dokümantasyonu

**eMuhasebe Pro - REST API v1**

Uygulamanın tüm operasyonlarını yapabileceğiniz REST API. Pagination, Validation ve Standardized Response'lar ile.

---

## 📋 İçindekiler

1. [API Versioning](#api-versioning)
2. [Authentication (İleride)](#authentication-ileride)
3. [Response Format](#response-format)
4. [Pagination](#pagination)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Endpoints](#endpoints)

---

## API Versioning

API versioning yapılır: `/api/v1/`

**Geçiş Planı:**
- **v0 (Legacy):** `/api/` → Deprecated, kaldırılacak
- **v1 (Current):** `/api/v1/` → Production ready
- **v2 (Future):** `/api/v2/` → Gelecere

**Backward Compatibility:**
- v1'deki tüm endpoint'ler yeni request/response format'ında
- v0 endpoint'leri deprecation warning ile çalışmaya devam ediyor (90 gün desteklenir)

---

## Authentication (İleride)

Şu anda authentication yok (public API).

**Future:** JWT token ile:
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {...}
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [
    {...},
    {...}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "message": "Müşteri bulunamadı",
    "code": "NOT_FOUND",
    "details": {
      "resource": "Müşteri",
      "id": 999
    }
  }
}
```

### Validation Error Response

```json
{
  "success": false,
  "error": {
    "message": "Validation hatası",
    "code": "VALIDATION_ERROR",
    "details": {
      "validation_errors": [
        {
          "field": "unvan",
          "message": "Min 2 karakter gerekli",
          "type": "string_too_short"
        },
        {
          "field": "email",
          "message": "Geçersiz email",
          "type": "value_error"
        }
      ]
    }
  }
}
```

---

## Pagination

Query parametresi ile sayfalama:

```
GET /api/v1/musteriler?page=2&per_page=50
```

**Parametreler:**
- `page`: Sayfa numarası (default: 1, min: 1)
- `per_page`: Sayfa başına kayıt sayısı (default: 20, min: 1, max: 100)

**Örnek Yanıt:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total": 235,
    "total_pages": 5,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Kod | Anlamı | Örnek |
|-----|--------|-------|
| **200** | OK | GET başarılı |
| **201** | Created | POST başarılı |
| **400** | Bad Request | Eksik/geçersiz field |
| **404** | Not Found | Kaynak yok |
| **409** | Conflict | Duplicate entry |
| **422** | Unprocessable Entity | Validation error |
| **429** | Too Many Requests | Rate limit |
| **500** | Internal Server Error | Sunucu hatası |

### Error Codes

| Code | Meaning | HTTP |
|------|---------|------|
| `NOT_FOUND` | Kaynak bulunamadı | 404 |
| `BAD_REQUEST` | Kötü istek | 400 |
| `VALIDATION_ERROR` | Input validation hatası | 422 |
| `DUPLICATE_ENTRY` | Aynı değer zaten var | 409 |
| `UNAUTHORIZED` | Yetkilendirme hatası | 401 |
| `FORBIDDEN` | İzin yok | 403 |
| `RATE_LIMIT_EXCEEDED` | Çok fazla istek | 429 |
| `INTERNAL_ERROR` | Sunucu hatası | 500 |

---

## Rate Limiting

Endpoint'lere göre farklı limitler:

| Endpoint | Limit | Pencere |
|----------|-------|--------|
| GET Listele | 30 | dakika |
| GET Detay | 60 | dakika |
| POST Oluştur | 10 | dakika |
| PUT Güncelle | 20 | dakika |
| DELETE Sil | 10 | dakika |

**Rate Limit Aşıldığında:**
```
HTTP/1.1 429 Too Many Requests

{
  "success": false,
  "error": {
    "message": "Çok fazla istek gönderdiniz. Lütfen daha sonra tekrar deneyiniz.",
    "code": "RATE_LIMIT_EXCEEDED"
  }
}
```

---

## Endpoints

### MÜŞTERİLER

#### 1. Müşterileri Listele

```
GET /api/v1/musteriler?page=1&per_page=20&q=abc
```

**Query Parameters:**
- `page` (int): Sayfa numarası
- `per_page` (int): Sayfa başına kayıt
- `q` (string): Arama keyword'ü

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "unvan": "ABC Ltd",
      "vergi_no": "1234567890",
      "email": "info@abc.com",
      "telefon": "+90 532 123 4567",
      "adres": "İstanbul, Türkiye"
    }
  ],
  "pagination": {...}
}
```

**Rate Limit:** 30/dakika

---

#### 2. Müşteri Detayı

```
GET /api/v1/musteriler/5
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "unvan": "ABC Ltd",
    "vergi_no": "1234567890",
    "email": "info@abc.com",
    "telefon": "+90 532 123 4567",
    "adres": "İstanbul, Türkiye"
  }
}
```

**Rate Limit:** 60/dakika

---

#### 3. Müşteri Oluştur

```
POST /api/v1/musteriler
Content-Type: application/json

{
  "unvan": "ABC Ltd",
  "vergi_no": "1234567890",
  "email": "info@abc.com",
  "telefon": "+90 532 123 4567",
  "adres": "İstanbul, Türkiye"
}
```

**Validation Rules:**
- `unvan` (required): string, min 2, max 255
- `vergi_no` (optional): 10-11 digit, sadece rakam
- `email` (optional): geçerli email format
- `telefon` (optional): max 20 karakter
- `adres` (optional): max 500 karakter

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 6,
    "unvan": "ABC Ltd",
    ...
  },
  "message": "Kayıt başarıyla oluşturuldu"
}
```

**Errors:**
- 400: `"unvan": "Min 2 karakter gerekli"`
- 409: `"Bu vergi numarası zaten kayıtlı"`
- 422: Validation error

**Rate Limit:** 10/dakika

---

#### 4. Müşteri Güncelle

```
PUT /api/v1/musteriler/5
Content-Type: application/json

{
  "unvan": "ABC Inc",
  "email": "newemail@abc.com"
}
```

**Not:** Tüm alanlar opsiyonel. Gönderilen alanlar güncellenir.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "unvan": "ABC Inc",
    "email": "newemail@abc.com",
    ...
  }
}
```

**Rate Limit:** 20/dakika

---

#### 5. Müşteri Sil

```
DELETE /api/v1/musteriler/5
```

**Response:**
```json
{
  "success": true,
  "message": "Müşteri başarıyla silindi",
  "data": {
    "id": 5
  }
}
```

**Rate Limit:** 10/dakika

---

### ÜRÜNLER

Ürünler için aynı pattern:

- `GET /api/v1/urunler` - Listele (30/dk)
- `GET /api/v1/urunler/{id}` - Detay (60/dk)
- `POST /api/v1/urunler` - Oluştur (10/dk)
- `PUT /api/v1/urunler/{id}` - Güncelle (20/dk)
- `DELETE /api/v1/urunler/{id}` - Sil (10/dk)

**Ürün Validation:**
```json
{
  "ad": "Laptop",
  "kod": "LT-001",
  "birim": "Adet",
  "alis_fiyat": 5000.00,
  "satis_fiyat": 6500.00,
  "stok_miktari": 10
}
```

- `ad` (required): min 2, max 255
- `kod` (optional): min 1, max 50
- `alis_fiyat` (required): > 0
- `satis_fiyat` (required): > 0
- `stok_miktari` (optional): >= 0

---

### FATURALAR

#### Alış Faturalarını Listele

```
GET /api/v1/faturalar/alis?page=1&per_page=20
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "fatura_no": "2026/ALI/001",
      "fatura_tarihi": "2026-03-26",
      "musteri_id": 1,
      "ara_toplam": 5000.00,
      "kdv_toplam": 900.00,
      "indirim_toplam": 0.00,
      "genel_toplam": 5900.00,
      "kalemler": [...],
      "notlar": "..."
    }
  ],
  "pagination": {...}
}
```

---

#### Alış Faturası Detayı

```
GET /api/v1/faturalar/alis/1
```

---

#### Fatura Dashboard Özeti

```
GET /api/v1/faturalar/ozet
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alis_count": 45,
    "satis_count": 78,
    "iade_count": 12
  }
}
```

---

### Satış ve İade Faturalar

Aynı pattern:
- `GET /api/v1/faturalar/satis` 
- `GET /api/v1/faturalar/satis/{id}`
- `GET /api/v1/faturalar/iade`
- `GET /api/v1/faturalar/iade/{id}`

---

## Arama Özellikleri

List endpoint'lerinde `?q=` ile arama:

```bash
# Müşteri araması
GET /api/v1/musteriler?q=ABC

# Ürün araması
GET /api/v1/urunler?q=laptop
```

**Response (Search):**
```json
{
  "success": true,
  "data": [...],
  "search": {
    "keyword": "ABC",
    "count": 5
  }
}
```

---

## Logging & Monitoring

Tüm API çağrıları otomatik olarak loglanır:

```
GET /api/v1/musteriler -> 200 (145ms)
POST /api/v1/musteriler -> 201 (245ms)
GET /api/v1/musteriler/999 -> 404 (32ms)
```

**Log Location:** `logs/app.log`, `logs/errors.log`

---

## Examples - cURL

### Müşteri Listesi

```bash
curl -X GET "http://localhost:5000/api/v1/musteriler?page=1&per_page=20" \
  -H "Content-Type: application/json"
```

### Müşteri Oluştur

```bash
curl -X POST http://localhost:5000/api/v1/musteriler \
  -H "Content-Type: application/json" \
  -d '{
    "unvan": "Acme Corporation",
    "vergi_no": "1234567890",
    "email": "contact@acme.com",
    "telefon": "+90 532 111 2222",
    "adres": "İstanbul, Türkiye"
  }'
```

### Müşteri Güncelle

```bash
curl -X PUT http://localhost:5000/api/v1/musteriler/5 \
  -H "Content-Type: application/json" \
  -d '{
    "unvan": "Acme Inc"
  }'
```

### Müşteri Sil

```bash
curl -X DELETE http://localhost:5000/api/v1/musteriler/5
```

---

## Examples - Python

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Müşteri Listesi
response = requests.get(
    f"{BASE_URL}/musteriler",
    params={"page": 1, "per_page": 20}
)
data = response.json()
print(data['data'])

# Müşteri Oluştur
response = requests.post(
    f"{BASE_URL}/musteriler",
    json={
        "unvan": "Test Co",
        "vergi_no": "1234567890",
        "email": "test@example.com"
    }
)
if response.status_code == 201:
    print("Müşteri oluşturuldu:", response.json()['data'])
else:
    print("Hata:", response.json()['error'])

# Müşteri Güncelle
response = requests.put(
    f"{BASE_URL}/musteriler/5",
    json={"unvan": "Test Inc"}
)
print(response.json())

# Müşteri Sil
response = requests.delete(f"{BASE_URL}/musteriler/5")
print(response.json())
```

---

## Maintenance & Support

- **API Status:** https://api.muhasebe.local/health (future)
- **Documentation:** [This file]
- **Issues:** GitHub Issues (future)
- **Versions:** Production (v1), Development (v2-coming)

---

**Son Güncelleme:** 2026-03-26  
**İŞ 4 Durumu:** ✅ COMPLETE (API v1 implementation + Pagination + Validation)
