# AgroVeri+ Canlıya Çıkış Yol Haritası

> **Proje:** AgroVeri+ — Organik Tarım Dijital Sertifika Doğrulama Platformu
> **Pilot Ortak:** ÇOFÜB (Çarşamba Organik Fındık Üreticileri Birliği), Samsun
> **Tarih:** Nisan 2026

---

## Mevcut Durum Analizi

| Bileşen | Durum | Not |
|---------|-------|-----|
| Frontend (HTML/CSS/JS) | ✅ Hazır | Backend API entegrasyonu + demo fallback |
| Backend (FastAPI) | ✅ Hazır | Async, PostgreSQL, modüler mimari |
| Veritabanı | ✅ Hazır | PostgreSQL + SQLAlchemy + Alembic |
| Kullanıcı Girişi | ✅ Hazır | JWT (register/login/refresh), 4 rol |
| CI/CD | ✅ Hazır | GitHub Actions (test + Docker build) |
| Docker | ✅ Hazır | Frontend + Backend + PostgreSQL |
| Test | ✅ Hazır | 35 test (auth, upload, verify, service) |
| Domain/SSL | ⏳ Bekliyor | Henüz alan adı alınmadı |
| IPFS Entegrasyonu | ⏳ Hazır | Pinata servisi yazıldı, API key ile aktif |
| GitHub Pages Demo | ✅ Yayında | Jüri erişimi için |

---

## Aşama 0 — Temel Hazırlık (1-2 Hafta)

**Hedef:** Projeyi canlıya çıkmaya hazır hale getirmek için eksik altyapıyı tamamla.

### 0.1 Versiyon Kontrol Düzeni
- [x] Git reposu oluştur
- [ ] `.gitignore` dosyası ekle
- [ ] Branch stratejisi belirle (`main` = production, `develop` = geliştirme)
- [ ] Commit mesaj kuralları belirle (Conventional Commits)

### 0.2 Proje Yapısı
```
agroveriplus/
├── frontend/            # Mevcut HTML/CSS/JS dosyaları
│   ├── index.html
│   └── demo.html
├── backend/             # FastAPI uygulaması (Aşama 2)
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/               # Reverse proxy yapılandırması
│   └── default.conf
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── deploy.yml
├── .gitignore
├── .env.example
└── README.md
```

### 0.3 Domain ve SSL
- [ ] Alan adı satın al (öneriler: `agroveri.plus`, `agroveriplus.com`, `agroveriplus.org`)
- [ ] DNS kayıtlarını yapılandır
- [ ] SSL sertifikası (Let's Encrypt ile ücretsiz — otomatik yenilenme)

---

## Aşama 1 — Statik Site Yayını (1 Hafta)

**Hedef:** Mevcut frontend'i canlıya al — backend olmadan da çalışan demo sürümü.

### Seçenek A: GitHub Pages (En Kolay — Ücretsiz)
```bash
# Repo ayarlarından GitHub Pages'i aktifleştir
# Settings → Pages → Source: main branch
# URL: https://tepikoglu.github.io/agroveriplus
```
**Artılar:** Ücretsiz, sıfır bakım, otomatik SSL
**Eksiler:** Sadece statik dosyalar, özel domain için ek ayar gerekir

### Seçenek B: Netlify / Vercel (Önerilen — Ücretsiz Tier)
```bash
# Netlify CLI ile:
npm install -g netlify-cli
netlify deploy --prod --dir=.

# Veya Vercel ile:
npm install -g vercel
vercel --prod
```
**Artılar:** Ücretsiz SSL, özel domain, otomatik deploy (push'ta), preview URL'ler
**Eksiler:** Ücretsiz tier sınırları var (Netlify: 100GB bant genişliği/ay)

### Seçenek C: Docker + VPS (İleri Seviye)
```bash
docker-compose up -d
```
**Artılar:** Tam kontrol, backend eklemeye hazır
**Eksiler:** VPS maliyeti (~$5-10/ay), bakım gerektirir

### Tavsiye
> **Hemen canlıya çıkmak için Seçenek B (Netlify)** ile başla.
> Backend hazır olduğunda **Seçenek C (Docker + VPS)** 'e geç.

---

## Aşama 2 — Backend Geliştirme (3-4 Hafta)

**Hedef:** Veri kalıcılığı sağla, gerçek bir API oluştur.

### 2.1 FastAPI Backend
```python
# Temel endpoint'ler:
POST   /api/certificates/upload     # Sertifika yükleme
POST   /api/certificates/verify     # Hash doğrulama
GET    /api/certificates/{hash}     # Sertifika detayı
GET    /api/health                  # Sağlık kontrolü
```

### 2.2 Veritabanı (PostgreSQL)
```sql
-- Temel tablolar:
certificates     -- Sertifika bilgileri + SHA-256 hash
farmers          -- Çiftçi/üretici bilgileri
verifications    -- Doğrulama logları (kim, ne zaman)
```

### 2.3 IPFS Entegrasyonu
- [ ] Pinata veya Infura IPFS servisi seç
- [ ] Sertifika yüklendiğinde IPFS'e pin'le
- [ ] IPFS CID'yi veritabanına kaydet
- [ ] QR kodda IPFS CID'yi de barındır

### 2.4 Temel Güvenlik
- [ ] CORS politikası yapılandır
- [ ] Rate limiting ekle (brute-force koruması)
- [ ] Dosya yükleme boyut ve tip kontrolü (backend tarafı)
- [ ] Input sanitizasyonu (SQL injection, XSS koruması)
- [ ] HTTPS zorunluluğu

---

## Aşama 3 — Kimlik Doğrulama ve Yetkilendirme (2 Hafta)

**Hedef:** Çiftçi ve tüketici girişi, rol bazlı erişim.

### 3.1 Kullanıcı Yönetimi
- [ ] Kayıt ve giriş sistemi (e-posta + şifre)
- [ ] JWT token tabanlı kimlik doğrulama
- [ ] Roller: `farmer` (üretici), `consumer` (tüketici), `certifier` (sertifika kuruluşu), `admin`
- [ ] Şifre sıfırlama akışı

### 3.2 Çiftçi Paneli
- [ ] Yüklenen sertifikaları listeleme
- [ ] Sertifika durumu takibi
- [ ] QR kod geçmişi

---

## Aşama 4 — Test ve Kalite Güvence (2 Hafta)

**Hedef:** Canlıya çıkmadan önce güvenilirlik sağla.

### 4.1 Test Piramidi
```
        /  E2E  \          ← Playwright / Cypress (kritik akışlar)
       /  Enteg. \         ← pytest (API endpoint testleri)
      /   Birim   \        ← pytest + jest (fonksiyon bazlı)
```

### 4.2 Minimum Test Kapsamı
- [ ] SHA-256 hash oluşturma doğruluğu
- [ ] QR kod üretme ve okuma döngüsü
- [ ] Sertifika yükleme → doğrulama akışı (uçtan uca)
- [ ] Geçersiz dosya/hash hata yönetimi
- [ ] API rate limiting testi

### 4.3 Performans
- [ ] Lighthouse skoru > 90 (tüm kategoriler)
- [ ] Mobil uyumluluk testi (çiftçiler büyük olasılıkla telefondan kullanacak)
- [ ] Yavaş bağlantı testi (kırsal bölge senaryosu)

---

## Aşama 5 — CI/CD Pipeline (1 Hafta)

**Hedef:** Her push'ta otomatik test, build ve deploy.

### 5.1 GitHub Actions Pipeline
```
Push → Lint → Test → Build → Deploy (staging) → Manuel onay → Deploy (production)
```

### 5.2 Ortamlar
| Ortam | URL | Amaç |
|-------|-----|-------|
| Development | `localhost:8080` | Yerel geliştirme |
| Staging | `staging.agroveriplus.com` | Test ve demo |
| Production | `agroveriplus.com` | Canlı sistem |

---

## Aşama 6 — Canlıya Çıkış (Production Deploy) (1 Hafta)

**Hedef:** Gerçek kullanıcılarla buluşma.

### 6.1 Altyapı Seçenekleri

#### Seçenek A: Hetzner Cloud (Bütçe Dostu — Önerilen)
| Kaynak | Fiyat | Açıklama |
|--------|-------|----------|
| CX22 VPS | ~€4.5/ay | 2 vCPU, 4GB RAM, 40GB SSD |
| Domain | ~€10/yıl | `.com` veya `.org` |
| **Toplam** | **~€65/yıl** | |

#### Seçenek B: DigitalOcean
| Kaynak | Fiyat | Açıklama |
|--------|-------|----------|
| Droplet | $6/ay | 1 vCPU, 1GB RAM, 25GB SSD |
| Domain | ~$12/yıl | |
| **Toplam** | **~$84/yıl** | |

#### Seçenek C: AWS (Ölçeklenebilir)
| Kaynak | Fiyat | Açıklama |
|--------|-------|----------|
| EC2 t3.micro | ~$8.5/ay | 1 yıl ücretsiz tier |
| RDS PostgreSQL | ~$15/ay | Yönetilen veritabanı |
| S3 + CloudFront | ~$1/ay | Statik dosyalar |
| **Toplam** | **~$25/ay** (sonra ~$295/yıl) | |

### 6.2 Önerilen Mimari (Production)
```
                    ┌─────────────┐
   İnternet ───────→│  Cloudflare │  (CDN + DDoS koruması + SSL)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Nginx    │  (Reverse Proxy + Static Files)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   FastAPI   │  (Uygulama Sunucusu)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──┐  ┌─────▼─────┐  ┌──▼──────┐
       │PostgreSQL│  │   IPFS    │  │  Redis  │
       │   (DB)   │  │ (Pinata)  │  │ (Cache) │
       └─────────┘  └───────────┘  └─────────┘
```

### 6.3 Canlıya Çıkış Kontrol Listesi
- [ ] Tüm testler geçiyor
- [ ] SSL sertifikası aktif
- [ ] Veritabanı yedeği ayarlandı (günlük otomatik)
- [ ] Hata izleme servisi aktif (Sentry)
- [ ] Uptime monitoring aktif (UptimeRobot — ücretsiz)
- [ ] `.env` dosyası production değerleriyle yapılandırıldı
- [ ] CORS sadece kendi domain'e izin veriyor
- [ ] Rate limiting aktif
- [ ] Loglar merkezi bir yere yazılıyor
- [ ] Geri dönüş (rollback) planı hazır

---

## Aşama 7 — İzleme ve Bakım (Sürekli)

### 7.1 İzleme Araçları
| Araç | Amaç | Maliyet |
|------|-------|---------|
| UptimeRobot | Uptime izleme | Ücretsiz (50 monitor) |
| Sentry | Hata yakalama | Ücretsiz (5K olay/ay) |
| Cloudflare Analytics | Trafik analizi | Ücretsiz |
| PostgreSQL pg_stat | DB performansı | Dahili |

### 7.2 Yedekleme Stratejisi
```bash
# Günlük otomatik veritabanı yedeği (cron job)
0 3 * * * pg_dump agroveriplus | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# 30 günlük yedek tutma
find /backups -name "*.sql.gz" -mtime +30 -delete
```

---

## Zaman Çizelgesi Özeti

```
Hafta  1-2   ██████████  Aşama 0: Temel Hazırlık + .gitignore, Docker, CI
Hafta  2-3   █████       Aşama 1: Statik Site Yayını (Netlify/GitHub Pages)
Hafta  3-7   ████████████████████  Aşama 2: Backend (FastAPI + PostgreSQL + IPFS)
Hafta  7-9   ██████████  Aşama 3: Kimlik Doğrulama
Hafta  9-11  ██████████  Aşama 4: Test ve Kalite
Hafta 11-12  █████       Aşama 5: CI/CD Pipeline
Hafta 12-13  █████       Aşama 6: Production Deploy
Hafta 13+    ▓▓▓▓▓▓▓▓▓▓  Aşama 7: İzleme ve Bakım (sürekli)
```

**Toplam tahmini süre:** ~13 hafta (3 ay)
**Hızlı başlangıç:** Statik site 1 hafta içinde canlıda olabilir

---

## Hızlı Başlangıç Komutları

### Yerel Geliştirme (Hemen Başla)
```bash
# Docker ile yerel çalıştırma
docker-compose up -d

# Tarayıcıda aç
open http://localhost:8080
```

### Netlify ile Anında Canlıya Al
```bash
# 1. Netlify CLI kur
npm install -g netlify-cli

# 2. Giriş yap
netlify login

# 3. Deploy et
netlify deploy --prod --dir=.

# Sonuç: https://agroveriplus.netlify.app (veya özel domain)
```

### GitHub Pages ile Canlıya Al
```
1. GitHub repo ayarlarına git
2. Settings → Pages
3. Source: "Deploy from a branch" seç
4. Branch: main, / (root) seç
5. Save
6. URL: https://tepikoglu.github.io/agroveriplus
```

---

## Maliyet Özeti (Yıllık)

| Senaryo | Maliyet | İçerik |
|---------|---------|--------|
| **MVP (Sadece Frontend)** | **€0** | GitHub Pages + Cloudflare |
| **Startup (Backend dahil)** | **~€65-100/yıl** | Hetzner VPS + Domain |
| **Ölçeklenebilir** | **~€300/yıl** | AWS/GCP yönetilen servisler |

---

## Sonraki Adımlar (Hemen Yapılabilecekler)

1. **Bu hafta:** Statik siteyi Netlify veya GitHub Pages'e deploy et
2. **Bu hafta:** Domain al ve DNS'i bağla
3. **Gelecek hafta:** FastAPI backend iskeletini oluştur
4. **2 hafta içinde:** PostgreSQL veritabanı şemasını tasarla
5. **1 ay içinde:** IPFS entegrasyonunu tamamla

---

*Bu yol haritası AgroVeri+ projesinin mevcut durumuna göre hazırlanmıştır. Her aşama tamamlandığında bir sonrakine geçilmelidir. Aşamalar arası bağımlılıklar göz önünde bulundurulmuştur.*
