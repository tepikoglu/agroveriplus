# Sprint 2 — Source Verification & Platform Growth

> **Süre:** 3 hafta (Nisan sonundan Mayıs ortasına)
> **Odak:** Phase 2 altyapısı — kaynak doğrulama, OAuth, parsel, dashboard
> **Önceki sprint:** Auth + JWT, CI/CD, backend API, 35 test

---

## Tamamlanan Sprint 1 Özeti

| Bileşen | Durum |
|---------|-------|
| FastAPI backend + PostgreSQL | ✅ |
| JWT auth (register/login/refresh) | ✅ |
| 4 rol (farmer, agronomist, cooperative_admin, analyst) | ✅ |
| Sertifika upload + SHA-256 + doğrulama | ✅ |
| IPFS pinning servisi (Pinata — API key ile aktif) | �� |
| Frontend ↔ Backend entegrasyonu (graceful fallback) | ✅ |
| CI/CD pipeline (test + Docker build) | ✅ |
| GitHub Pages demo (jüri erişimi) | ✅ |
| 35 test (auth, upload, verify, service) | ✅ |

## Sprint 2 İlerleme Durumu

| Bileşen | Durum | Test |
|---------|-------|------|
| Parsel modeli + CRUD + EUDR summary | ✅ | 9 |
| Sertifika metadata güncelleme | ✅ | 3 |
| Sertifika ↔ Parsel bağlantısı | ✅ | — |
| Dış kayıt sorgusu (OTBIS/ECOCERT/ETKO mock) | ✅ | 4 |
| Dashboard stats endpoint | ✅ | 3 |
| Bildirim sistemi (model + servis + endpoint) | ✅ | 7 |
| EN/TR dil desteği (index + demo) | ✅ | — |
| Google OAuth | ⏳ Sprint 3 | — |
| Frontend dashboard sayfası | ⏳ Sprint 3 | — |
| **Toplam test** | **61 passing** | |

---

## Sprint 2 Hedefleri

```
Hafta 1   ████████  OAuth + Parsel modeli + Dashboard iskeleti
Hafta 2   ████████  Sertifika detay ekranı + Dış kayıt sorgusu
Hafta 3   ████████  EUDR DDS hazırlık + Test + Stabilizasyon
```

---

## Hafta 1 — OAuth, Parsel Modeli, Dashboard

### 1.1 Google OAuth Entegrasyonu

**Neden:** Çiftçiler ve kooperatif yöneticileri için sosyal giriş — şifre hatırlama derdi yok.

**Dosyalar:**
```
backend/app/routes/auth.py        → POST /api/auth/google  (yeni endpoint)
backend/app/services/oauth.py     → Google ID token doğrulama (yeni dosya)
backend/app/models/user.py        → oauth_provider + oauth_id alanları aktif et
```

**Akış:**
```
Frontend: Google Sign-In butonuna tıkla
    → Google ID token al
    → POST /api/auth/google { id_token: "..." }
    → Backend: token'ı Google'dan doğrula
    → Kullanıcı yoksa oluştur (auto-register)
    → access_token + refresh_token dön
```

**Env değişkenleri:**
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...    # opsiyonel, sadece server-side flow için
```

**Kabul kriterleri:**
- [ ] Google ile giriş yapılabiliyor
- [ ] İlk girişte otomatik kayıt (role: farmer varsayılan)
- [ ] Mevcut email ile eşleşirse hesaplar birleşiyor
- [ ] Test: 5+ yeni test

---

### 1.2 Parsel (Arazi) Modeli

**Neden:** "5 hektar tarladan 500 ton ürün" dolandırıcılığına karşı — EUDR de bunu zorunlu kılacak.

**Yeni model:**
```python
# backend/app/models/parcel.py
class Parcel(Base):
    __tablename__ = "parcels"

    id: UUID
    farmer_id: UUID (FK → users)
    name: str                       # "Çarşamba Fındık Bahçesi"
    location_lat: float
    location_lon: float
    area_hectares: float
    crop_type: str                  # "hazelnut", "olive", "wheat"
    province: str                   # "Samsun"
    district: str                   # "Çarşamba"

    # Gelecek sprint: uydu doğrulaması
    # sentinel_verified: bool
    # ndvi_score: float
    # last_satellite_check: datetime

    created_at: datetime
```

**Yeni endpoint'ler:**
```
POST   /api/parcels                  → Parsel ekle (farmer, coop_admin)
GET    /api/parcels                  → Kendi parsellerini listele
GET    /api/parcels/{id}             → Parsel detayı
PUT    /api/parcels/{id}             → Güncelle
DELETE /api/parcels/{id}             → Sil (soft delete)
```

**İlişki:** Certificate ↔ Parcel (bir sertifika bir parsele bağlanabilir)
```python
# certificate.py'ye ekle:
parcel_id: UUID | None (FK → parcels)
```

**Kabul kriterleri:**
- [ ] Parsel CRUD çalışıyor
- [ ] Sertifika yüklerken opsiyonel parsel seçilebiliyor
- [ ] Sadece farmer ve cooperative_admin parsel ekleyebilir
- [ ] Test: 8+ yeni test

---

### 1.3 Dashboard İskeleti

**Neden:** Her rolün farklı bir görünüme ihtiyacı var.

**Yeni dosya:** `dashboard.html`

| Rol | Gördükleri |
|-----|-----------|
| **farmer** | Kendi sertifikaları, parselleri, QR kodları |
| **cooperative_admin** | Kooperatif üyelerinin sertifikaları, toplu istatistik |
| **agronomist** | Doğrulama geçmişi, şüpheli sertifikalar |
| **analyst** | Tüm veriler, dışa aktarma, grafikler |

**Sprint 2'de sadece iskelet:**
- [ ] Login sonrası dashboard'a yönlendir
- [ ] Role göre farklı bölümler göster/gizle
- [ ] Kendi sertifikalarımı listele (farmer)
- [ ] Basit istatistik kartları (toplam sertifika, doğrulama sayısı)

**Backend endpoint:**
```
GET /api/dashboard/stats    → { total_certs, total_verifications, my_certs, my_parcels }
```

---

## Hafta 2 — Sertifika Detay & Dış Kayıt Sorgusu

### 2.1 Sertifika Metadata Zenginleştirme

**Neden:** Yüklenen sertifikada şu an sadece dosya bilgisi var. Sertifika kuruluşu, ürün tipi, geçerlilik tarihi gibi alanlar boş.

**Yeni endpoint:**
```
PUT /api/certificates/{id}/metadata
{
    "certifier_name": "ECOCERT",
    "certificate_number": "TR-BIO-001-2026",
    "product_type": "Organic Hazelnut",
    "valid_from": "2026-01-15",
    "valid_until": "2027-01-14",
    "parcel_id": "uuid..."
}
```

**Kabul kriterleri:**
- [ ] Upload sonrası metadata ekleme ekranı (frontend)
- [ ] Doğrulama ekranında metadata gösteriliyor (certifier, product, validity)
- [ ] Süresi geçmiş sertifikalar sarı uyarı ile gösteriliyor

---

### 2.2 Dış Kayıt Sorgusu (Hazırlık)

**Neden:** Phase 2'nin kalbi — sertifikayı dış veritabanlarıyla çapraz kontrol.

**Mimari:**
```python
# backend/app/services/external_registry.py

class RegistryProvider(Protocol):
    """Her dış kaynak bu interface'i implemente eder."""
    async def verify(self, certificate_number: str, certifier: str) -> RegistryResult

class RegistryResult:
    source: str                    # "OTBIS", "ECOCERT", "ETKO"
    found: bool
    status: str                    # "valid", "expired", "revoked", "not_found"
    details: dict | None

# Sağlayıcılar:
class OTBISProvider(RegistryProvider): ...    # Türk organik DB
class ECOCERTProvider(RegistryProvider): ...  # Uluslararası
class ETKOProvider(RegistryProvider): ...     # Türk sertifika kuruluşu
class MockProvider(RegistryProvider): ...     # Test/demo için
```

**Sprint 2'de:**
- [ ] `RegistryProvider` interface'i ve `MockProvider` oluştur
- [ ] `GET /api/certificates/{id}/external-check` endpoint'i
- [ ] Demo'da mock sonuçları göster (gerçek API entegrasyonu Sprint 3'te)
- [ ] Her sorgu `external_checks` tablosuna loglanır

**Yeni model:**
```python
class ExternalCheck(Base):
    __tablename__ = "external_checks"

    id: UUID
    certificate_id: UUID (FK)
    provider: str                  # "OTBIS", "ECOCERT", "ETKO"
    status: str                    # "valid", "expired", "revoked", "not_found", "error"
    raw_response: JSON | None
    checked_at: datetime
```

---

## Hafta 3 — EUDR, Stabilizasyon, Test

### 3.1 EUDR DDS Hazırlık

**Neden:** AB Ormansızlaşma Yönetmeliği (EUDR) 2025'te yürürlükte. Due Diligence Statement (DDS) için geolocasyon zorunlu.

**Ne yapılacak:**
- [ ] Parsel modeline EUDR zorunlu alanları ekle:
  ```python
  geojson_polygon: JSON | None     # Parsel sınırları (GeoJSON)
  country_of_production: str
  commodity_code: str               # HS kodu (0802.22 = fındık)
  ```
- [ ] `GET /api/parcels/{id}/eudr-summary` → DDS'e hazır veri paketi
- [ ] Frontend'de parsel haritası gösterimi (Leaflet.js)

---

### 3.2 Bildirim Sistemi (Webhook Hazırlık)

**Neden:** Kooperatif yöneticisi bir çiftçi sertifika yüklediğinde bilmeli.

**Sprint 2'de sadece mimari:**
```python
# backend/app/services/notifications.py

class NotificationEvent(str, Enum):
    certificate_uploaded = "certificate_uploaded"
    certificate_verified = "certificate_verified"
    certificate_expired = "certificate_expired"
    external_check_failed = "external_check_failed"

async def notify(event: NotificationEvent, data: dict):
    """Gelecekte: email, push, webhook. Şimdilik DB'ye log."""
    ...
```

**Yeni model:**
```python
class Notification(Base):
    __tablename__ = "notifications"

    id: UUID
    user_id: UUID (FK)
    event: str
    title: str
    body: str
    is_read: bool = False
    created_at: datetime
```

**Endpoint'ler:**
```
GET  /api/notifications              → Okunmamış bildirimler
POST /api/notifications/{id}/read    → Okundu işaretle
```

---

### 3.3 Test & Stabilizasyon

**Hedef test sayısı:** 35 → 70+

| Alan | Yeni Test Sayısı |
|------|-----------------|
| OAuth (Google) | 5 |
| Parsel CRUD | 8 |
| Dashboard stats | 4 |
| Sertifika metadata | 5 |
| External registry (mock) | 6 |
| Notifications | 4 |
| Yetkilendirme (rol bazlı) | 5 |
| **Toplam yeni** | **~37** |

---

## Veritabanı Şema Evrimi (Sprint 2 Sonu)

```
users ──────────┐
  │              │
  ├── parcels    │
  │     │        │
  │     └── certificates ──── external_checks
  │              │
  │              └── verifications
  │
  └── notifications
```

---

## API Endpoint Özeti (Sprint 2 Sonu)

```
# Auth (mevcut + OAuth)
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/google                    ← YENİ
GET    /api/auth/me

# Certificates (mevcut + metadata)
POST   /api/certificates/upload
POST   /api/certificates/verify
GET    /api/certificates/{hash}
PUT    /api/certificates/{id}/metadata     ← YENİ
GET    /api/certificates/{id}/external-check  ← YENİ

# Parcels (tamamen yeni)
POST   /api/parcels                        ← YENİ
GET    /api/parcels                        ← YENİ
GET    /api/parcels/{id}                   ← YENİ
PUT    /api/parcels/{id}                   ← YENİ
DELETE /api/parcels/{id}                   ← YENİ
GET    /api/parcels/{id}/eudr-summary      ← YENİ

# Dashboard (yeni)
GET    /api/dashboard/stats                ← YENİ

# Notifications (yeni)
GET    /api/notifications                  ← YENİ
POST   /api/notifications/{id}/read       ← YENİ

# Health
GET    /api/health
```

---

## Sprint 3 Ön Bakış (Mayıs ortası–Haziran)

| Özellik | Açıklama |
|---------|----------|
| Gerçek OTBIS entegrasyonu | T.C. Tarım Bakanlığı API'sine bağlan |
| ECOCERT registry sorgusu | Uluslararası sertifika doğrulama |
| Sentinel-2 uydu entegrasyonu | NDVI analizi ile parsel kapasite kontrolü |
| EUDR DDS oluşturma | PDF/JSON olarak DDS dışa aktarma |
| Email bildirimleri | Sertifika durumu değiştiğinde email |
| Admin paneli | Kullanıcı yönetimi, sistem istatistikleri |
| Mobil optimizasyon | PWA (Progressive Web App) desteği |
| Türkçe lokalizasyon | UI çevirisi + çok dil altyapısı |

---

## Teknik Borç (Sprint 2'de Temizlenecek)

- [ ] PBKDF2 → bcrypt/argon2 geçişi (production Dockerfile'da)
- [ ] stdlib JWT → PyJWT geçişi (production'da cryptography mevcut)
- [ ] Rate limiting middleware (slowapi)
- [ ] Request logging middleware
- [ ] Alembic migration'ları oluştur (şu an auto-create)
- [ ] .env.example güncelle (yeni değişkenler)

---

*Sprint 2 planı AgroVeri+ projesinin mevcut durumuna göre hazırlanmıştır.
Her hafta sonunda retrospektif yapılması ve planın gerektiğinde ayarlanması önerilir.*
