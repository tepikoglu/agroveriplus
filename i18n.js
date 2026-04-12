const I18N = {
  en: {
    // Nav
    "nav.problem": "Problem",
    "nav.solution": "Solution",
    "nav.defense": "Defense",
    "nav.roadmap": "Roadmap",
    "nav.faq": "FAQ",
    "nav.contact": "Contact",
    "nav.demo": "Demo",

    // Hero
    "hero.tag": "Digital Traceability for Organic Agriculture",
    "hero.h1": 'Every Certificate. <em>Verified.</em><br>Immutable.',
    "hero.p": "AgroVeri+ secures organic supply chains with IPFS-backed document integrity, cross-database verification, and satellite-powered volume validation.",
    "hero.btn1": "Demo →",
    "hero.btn2": "See the Problem",

    // Stats
    "stat.1": "tonnes flagged suspicious",
    "stat.2": "annual fraud damage in EU",
    "stat.3": "fraud growth in organics",
    "stat.4": "ePhyto countries",

    // Problem
    "problem.tag": "The Problem",
    "problem.h2": 'Organic fraud is a <em style="color:var(--red)">billion-euro</em> industry',
    "problem.p": "Fake documents, shell certifiers, and transit-country laundering cost legitimate farmers billions.",
    "case1.title": "Chilean Raspberry Scheme",
    "case1.p": "$12M organic raspberries from China re-documented as Chilean.",
    "case2.title": "The Pistachio Cartel",
    "case2.p": "Spanish OCG sold conventional pistachios at 80% premium with forged certifications.",
    "case3.title": "Rotten Apple Network",
    "case3.p": "Mycotoxin-contaminated apples rebranded as organic European products.",

    // Solution
    "solution.tag": "Our Solution",
    "solution.h2": 'Three pillars of <em style="color:var(--gold)">trust</em>',
    "pillar1.title": "Document Integrity",
    "pillar1.p": "IPFS hashing locks every certificate. One pixel change = new hash.",
    "pillar2.title": "Source Verification",
    "pillar2.p": "Cross-reference against OTBIS, ECOCERT, and ePhyto Hub.",
    "pillar3.title": "Volume Validation",
    "pillar3.p": "Satellite imagery calculates real production capacity.",

    // Defense
    "defense.tag": "Fraud vs. Defense",
    "defense.h2": 'Five threats. <em style="color:var(--emerald)">Five defenses.</em>',
    "defense.p": "We studied real fraud methods — then built countermeasures.",
    "t1.title": "Transit Laundering",
    "t1.p": "Product travels Iran→UAE→EU with fabricated paperwork.",
    "d1.p": "Origin inconsistency flags impossible commodity origins.",
    "t2.title": "Forged Certificates",
    "t2.p": "Photoshop certificates and shell certification bodies.",
    "d2.p": "IPFS hash + ECOCERT/IMO/ETKO registry cross-reference.",
    "t3.title": "Ghost Production",
    "t3.p": "5ha farm declares 500 tonnes via fake records.",
    "d3.p": "Satellite parcel analysis calculates max capacity.",
    "t4.title": "Paper Phytosanitary",
    "t4.p": "Paper certificates trivially forged at customs.",
    "d4.p": "ePhyto Hub + TRACES-NT real-time verification.",
    "t5.title": "Crime Networks",
    "t5.p": "OCGs control certifiers, importers, entry points.",
    "d5.p": "Multi-point cross-checks impossible to circumvent.",

    // Architecture
    "arch.tag": "Architecture",
    "arch.h2": "Four layers of defense",
    "layer1.title": "Document Integrity",
    "layer1.i1": "✓ IPFS hash — immutable fingerprint",
    "layer1.i2": "✓ Timestamp + uploader identity",
    "layer1.i3": "✓ Verified unaltered since upload",
    "layer2.title": "Source Verification",
    "layer2.i1": "○ ECOCERT/IMO/ETKO registry",
    "layer2.i2": "○ OTBIS database match",
    "layer2.i3": "○ ePhyto Hub + TRACES-NT",
    "layer3.title": "Quantity Validation",
    "layer3.i1": "○ Satellite max production",
    "layer3.i2": "○ Volume vs. possibility",
    "layer3.i3": "○ Anomaly detection",
    "layer4.title": "AI Analysis",
    "layer4.i1": "○ Format validation",
    "layer4.i2": "○ Cross-reference consistency",
    "layer4.i3": "○ Duplicate detection",

    // How it works
    "how.tag": "How It Works",
    "how.h2": 'Three steps to <em style="color:var(--emerald)">trust</em>',
    "step1.title": "Upload",
    "step1.p": "Upload organic or phytosanitary certificate.",
    "step2.title": "Hash & Seal",
    "step2.p": "IPFS hash with identity, GPS, timestamp.",
    "step3.title": "Verify",
    "step3.p": "Cross-check OTBIS, ePhyto, satellite data.",

    // Built for
    "for.tag": "Built For",
    "for.h2": "Who uses AgroVeri+?",
    "persona1.title": "Cooperatives",
    "persona1.p": "Verify member certifications from one dashboard.",
    "persona2.title": "Certifiers",
    "persona2.p": "Upload directly to an immutable system.",
    "persona3.title": "Importers",
    "persona3.p": "EUDR-ready farm-to-port traceability.",
    "persona4.title": "Regulators",
    "persona4.p": "Real-time monitoring and volume checks.",

    // Roadmap
    "rm.tag": "Roadmap",
    "rm.h2": 'Building trust, <em style="color:var(--gold)">phase by phase</em>',
    "rm1.title": "Document Integrity",
    "rm1.i1": "✓ IPFS immutability",
    "rm1.i2": "✓ Timestamp & identity",
    "rm1.i3": "✓ QR code per product",
    "rm1.i4": "✓ Certificate viewer",
    "rm2.title": "Source Verification",
    "rm2.i1": "○ OTBIS API",
    "rm2.i2": "○ Certifier cross-check",
    "rm2.i3": "○ ePhyto Hub",
    "rm2.i4": "○ EUDR DDS prep",
    "rm3.title": "AI & Satellite",
    "rm3.i1": "○ AI format analysis",
    "rm3.i2": "○ Satellite validation",
    "rm3.i3": "○ Anomaly detection",
    "rm3.i4": "○ Risk scoring",

    // FAQ
    "faq.tag": "FAQ",
    "faq.h2": 'Tough questions, <em style="color:var(--emerald)">honest answers</em>',
    "faq1.q": "Can AgroVeri+ detect fake certificates?",
    "faq1.a": "Phase 1: integrity. Phase 2: source verification via ECOCERT/IMO + OTBIS. Phase 3: AI format analysis.",
    "faq2.q": "What about garbage in, garbage out?",
    "faq2.a": "Phase 2 solves this — certification bodies upload directly, preventing fake documents from entering.",
    "faq3.q": "How does IPFS hashing work?",
    "faq3.a": "Cryptographic hash per document. One pixel change = different hash. Distributed and permanent.",
    "faq4.q": "Is AgroVeri+ EUDR-compliant?",
    "faq4.a": "Yes — plot-level geolocation, traceability, and DDS preparation for Dec 2026 / June 2027 deadlines.",

    // CTA
    "cta.tag": "Get in Touch",
    "cta.h2": 'Ready to make your supply chain <em>fraud-proof</em>?',
    "cta.p": "Upload a certificate, seal it with IPFS, generate a QR code — try it now.",
    "cta.btn": "Try the Demo →",

    // Footer
    "footer.desc": "Digital traceability for organic agriculture.",
    "footer.platform": "Platform",
    "footer.integrations": "Integrations",
    "footer.contact": "Contact",

    // Demo page
    "demo.farmer": "Farmer",
    "demo.consumer": "Consumer",
    "demo.back": "← Back to site",
    "demo.step1": "Upload",
    "demo.step2": "Seal",
    "demo.step3": "QR Code",
    "demo.upload.title": "Upload Certificate",
    "demo.upload.desc": "Upload your organic certificate. A cryptographic seal will be generated and you'll receive a verifiable QR code.",
    "demo.upload.drop": "Drop your certificate here",
    "demo.upload.hint": "PDF, JPG, PNG — Max 10 MB",
    "demo.upload.choose": "Choose File",
    "demo.upload.photo": "Take Photo",
    "demo.seal.title": "Digital Seal",
    "demo.seal.loading": "Generating hash...",
    "demo.seal.label": "SHA-256 Digital Seal",
    "demo.seal.copy": "Copy",
    "demo.seal.btn": "Generate QR Code",
    "demo.qr.title": "Your QR Code is Ready",
    "demo.qr.desc": "Attach this QR code to your product packaging. Consumers can scan it to verify your certificate.",
    "demo.qr.download": "Download",
    "demo.qr.share": "Share",
    "demo.qr.info1": "Your certificate is now digitally sealed.",
    "demo.qr.info2": "This seal is immutable — backed by cryptographic proof.",
    "demo.qr.info3": "Consumers verify authenticity by scanning the QR code.",
    "demo.qr.new": "Upload New Certificate",
    "demo.scan.title": "Scan QR Code",
    "demo.scan.desc": "Point your camera at the AgroVeri+ QR code on the product.",
    "demo.scan.open": "Open Camera",
    "demo.scan.close": "Close Camera",
    "demo.scan.or": "— or enter hash manually —",
    "demo.scan.placeholder": "Paste hash code here...",
    "demo.scan.verify": "Verify",
    "demo.result.ok.title": "Verified",
    "demo.result.ok.desc": "This certificate is authentic and has not been altered.",
    "demo.result.fail.title": "Not Verified",
    "demo.result.fail.desc": "This certificate was not found in the system. Request the original from your supplier.",
    "demo.result.details": "Certificate Details",
    "demo.result.trust": "Trust Layer",
    "demo.result.intact": "Digital seal intact",
    "demo.result.another": "Scan Another QR",
  },

  tr: {
    // Nav
    "nav.problem": "Sorun",
    "nav.solution": "Çözüm",
    "nav.defense": "Savunma",
    "nav.roadmap": "Yol Haritası",
    "nav.faq": "SSS",
    "nav.contact": "İletişim",
    "nav.demo": "Demo",

    // Hero
    "hero.tag": "Organik Tarım İçin Dijital İzlenebilirlik",
    "hero.h1": 'Her Sertifika. <em>Doğrulanmış.</em><br>Değiştirilemez.',
    "hero.p": "AgroVeri+ organik tedarik zincirlerini IPFS destekli belge bütünlüğü, çapraz veritabanı doğrulaması ve uydu tabanlı hacim kontrolü ile güvence altına alır.",
    "hero.btn1": "Demo →",
    "hero.btn2": "Sorunu Gör",

    // Stats
    "stat.1": "ton şüpheli olarak işaretlendi",
    "stat.2": "AB'de yıllık sahtecilik zararı",
    "stat.3": "organiklerde sahtecilik artışı",
    "stat.4": "ePhyto ülkesi",

    // Problem
    "problem.tag": "Sorun",
    "problem.h2": 'Organik sahtecilik <em style="color:var(--red)">milyar euroluk</em> bir sektör',
    "problem.p": "Sahte belgeler, paravan sertifika kuruluşları ve transit ülke aklaması meşru çiftçilere milyarlara mal oluyor.",
    "case1.title": "Şili Ahududu Planı",
    "case1.p": "Çin'den gelen 12 milyon dolarlık organik ahududu Şili menşeili olarak belgelendi.",
    "case2.title": "Antep Fıstığı Karteli",
    "case2.p": "İspanyol suç örgütü konvansiyonel antep fıstığını sahte sertifikayla %80 primle sattı.",
    "case3.title": "Çürük Elma Şebekesi",
    "case3.p": "Mikotoksinli elmalar organik Avrupa ürünü olarak yeniden etiketlendi.",

    // Solution
    "solution.tag": "Çözümümüz",
    "solution.h2": 'Güvenin <em style="color:var(--gold)">üç sütunu</em>',
    "pillar1.title": "Belge Bütünlüğü",
    "pillar1.p": "IPFS hash'leme her sertifikayı kilitler. Bir piksel değişiklik = yeni hash.",
    "pillar2.title": "Kaynak Doğrulama",
    "pillar2.p": "OTBIS, ECOCERT ve ePhyto Hub ile çapraz kontrol.",
    "pillar3.title": "Hacim Doğrulama",
    "pillar3.p": "Uydu görüntüleri gerçek üretim kapasitesini hesaplar.",

    // Defense
    "defense.tag": "Sahtecilik vs. Savunma",
    "defense.h2": 'Beş tehdit. <em style="color:var(--emerald)">Beş savunma.</em>',
    "defense.p": "Gerçek sahtecilik yöntemlerini inceledik — sonra karşı önlemleri geliştirdik.",
    "t1.title": "Transit Aklama",
    "t1.p": "Ürün sahte evraklarla İran→BAE→AB rotasında seyahat ediyor.",
    "d1.p": "Menşe tutarsızlık bayrakları imkansız emtia kökenlerini işaretler.",
    "t2.title": "Sahte Sertifikalar",
    "t2.p": "Photoshop sertifikaları ve paravan sertifika kuruluşları.",
    "d2.p": "IPFS hash + ECOCERT/IMO/ETKO kayıt çapraz kontrolü.",
    "t3.title": "Hayalet Üretim",
    "t3.p": "5 hektarlık çiftlik sahte kayıtlarla 500 ton beyan ediyor.",
    "d3.p": "Uydu parsel analizi maksimum kapasiteyi hesaplar.",
    "t4.title": "Kağıt Bitki Sağlığı",
    "t4.p": "Kağıt sertifikalar gümrükte kolayca taklit ediliyor.",
    "d4.p": "ePhyto Hub + TRACES-NT gerçek zamanlı doğrulama.",
    "t5.title": "Suç Şebekeleri",
    "t5.p": "Organize suç örgütleri sertifikacıları, ithalatçıları, giriş noktalarını kontrol ediyor.",
    "d5.p": "Çok noktalı çapraz kontrolleri atlatmak imkansız.",

    // Architecture
    "arch.tag": "Mimari",
    "arch.h2": "Dört katmanlı savunma",
    "layer1.title": "Belge Bütünlüğü",
    "layer1.i1": "✓ IPFS hash — değiştirilemez parmak izi",
    "layer1.i2": "✓ Zaman damgası + yükleyici kimliği",
    "layer1.i3": "✓ Yüklenmeden bu yana değişmediği doğrulandı",
    "layer2.title": "Kaynak Doğrulama",
    "layer2.i1": "○ ECOCERT/IMO/ETKO kayıt kontrolü",
    "layer2.i2": "○ OTBIS veritabanı eşleştirme",
    "layer2.i3": "○ ePhyto Hub + TRACES-NT",
    "layer3.title": "Miktar Doğrulama",
    "layer3.i1": "○ Uydu maksimum üretim",
    "layer3.i2": "○ Hacim vs. olasılık",
    "layer3.i3": "○ Anomali tespiti",
    "layer4.title": "Yapay Zeka Analizi",
    "layer4.i1": "○ Format doğrulama",
    "layer4.i2": "○ Çapraz referans tutarlılığı",
    "layer4.i3": "○ Kopya tespiti",

    // How it works
    "how.tag": "Nasıl Çalışır",
    "how.h2": '<em style="color:var(--emerald)">Güvene</em> üç adım',
    "step1.title": "Yükle",
    "step1.p": "Organik veya bitki sağlığı sertifikasını yükle.",
    "step2.title": "Hashle ve Mühürle",
    "step2.p": "IPFS hash + kimlik, GPS, zaman damgası.",
    "step3.title": "Doğrula",
    "step3.p": "OTBIS, ePhyto, uydu verileriyle çapraz kontrol.",

    // Built for
    "for.tag": "Kimler İçin",
    "for.h2": "AgroVeri+ kimler kullanıyor?",
    "persona1.title": "Kooperatifler",
    "persona1.p": "Üye sertifikalarını tek panelden doğrulayın.",
    "persona2.title": "Sertifikacılar",
    "persona2.p": "Doğrudan değiştirilemez sisteme yükleyin.",
    "persona3.title": "İthalatçılar",
    "persona3.p": "EUDR uyumlu çiftlikten limana izlenebilirlik.",
    "persona4.title": "Düzenleyiciler",
    "persona4.p": "Gerçek zamanlı izleme ve hacim kontrolleri.",

    // Roadmap
    "rm.tag": "Yol Haritası",
    "rm.h2": 'Güveni <em style="color:var(--gold)">aşama aşama</em> inşa etmek',
    "rm1.title": "Belge Bütünlüğü",
    "rm1.i1": "✓ IPFS değişmezlik",
    "rm1.i2": "✓ Zaman damgası ve kimlik",
    "rm1.i3": "✓ Ürün başına QR kod",
    "rm1.i4": "✓ Sertifika görüntüleyici",
    "rm2.title": "Kaynak Doğrulama",
    "rm2.i1": "○ OTBIS API",
    "rm2.i2": "○ Sertifikacı çapraz kontrol",
    "rm2.i3": "○ ePhyto Hub",
    "rm2.i4": "○ EUDR DDS hazırlık",
    "rm3.title": "Yapay Zeka ve Uydu",
    "rm3.i1": "○ Yapay zeka format analizi",
    "rm3.i2": "○ Uydu doğrulama",
    "rm3.i3": "○ Anomali tespiti",
    "rm3.i4": "○ Risk puanlama",

    // FAQ
    "faq.tag": "SSS",
    "faq.h2": 'Zor sorular, <em style="color:var(--emerald)">dürüst cevaplar</em>',
    "faq1.q": "AgroVeri+ sahte sertifikaları tespit edebilir mi?",
    "faq1.a": "Faz 1: bütünlük. Faz 2: ECOCERT/IMO + OTBIS ile kaynak doğrulama. Faz 3: yapay zeka format analizi.",
    "faq2.q": "Çöp girerse çöp çıkar sorunu ne olacak?",
    "faq2.a": "Faz 2 bunu çözer — sertifika kuruluşları doğrudan yükler, sahte belgelerin sisteme girmesini engeller.",
    "faq3.q": "IPFS hash'leme nasıl çalışır?",
    "faq3.a": "Belge başına kriptografik hash. Bir piksel değişiklik = farklı hash. Dağıtık ve kalıcı.",
    "faq4.q": "AgroVeri+ EUDR uyumlu mu?",
    "faq4.a": "Evet — parsel düzeyinde coğrafi konum, izlenebilirlik ve Aralık 2026 / Haziran 2027 son tarihleri için DDS hazırlığı.",

    // CTA
    "cta.tag": "İletişim",
    "cta.h2": 'Tedarik zincirinizi <em>sahteciliğe karşı</em> korumaya hazır mısınız?',
    "cta.p": "Sertifika yükle, IPFS ile mühürle, QR kod oluştur — hemen deneyin.",
    "cta.btn": "Demo'yu Dene →",

    // Footer
    "footer.desc": "Organik tarım için dijital izlenebilirlik.",
    "footer.platform": "Platform",
    "footer.integrations": "Entegrasyonlar",
    "footer.contact": "İletişim",

    // Demo page
    "demo.farmer": "Çiftçi",
    "demo.consumer": "Tüketici",
    "demo.back": "← Siteye Dön",
    "demo.step1": "Yükle",
    "demo.step2": "Mühürle",
    "demo.step3": "QR Kod",
    "demo.upload.title": "Sertifika Yükle",
    "demo.upload.desc": "Organik sertifikanızı yükleyin. Kriptografik mühür oluşturulacak ve doğrulanabilir QR kod alacaksınız.",
    "demo.upload.drop": "Sertifikanızı buraya bırakın",
    "demo.upload.hint": "PDF, JPG, PNG — Maks. 10 MB",
    "demo.upload.choose": "Dosya Seç",
    "demo.upload.photo": "Fotoğraf Çek",
    "demo.seal.title": "Dijital Mühür",
    "demo.seal.loading": "Hash oluşturuluyor...",
    "demo.seal.label": "SHA-256 Dijital Mühür",
    "demo.seal.copy": "Kopyala",
    "demo.seal.btn": "QR Kod Oluştur",
    "demo.qr.title": "QR Kodunuz Hazır",
    "demo.qr.desc": "Bu QR kodu ürün ambalajınıza yapıştırın. Tüketiciler sertifikanızı tarayarak doğrulayabilir.",
    "demo.qr.download": "İndir",
    "demo.qr.share": "Paylaş",
    "demo.qr.info1": "Sertifikanız artık dijital olarak mühürlendi.",
    "demo.qr.info2": "Bu mühür değiştirilemez — kriptografik kanıtla desteklenir.",
    "demo.qr.info3": "Tüketiciler QR kodu tarayarak özgünlüğü doğrular.",
    "demo.qr.new": "Yeni Sertifika Yükle",
    "demo.scan.title": "QR Kod Tara",
    "demo.scan.desc": "Kameranızı üründeki AgroVeri+ QR koduna doğrultun.",
    "demo.scan.open": "Kamerayı Aç",
    "demo.scan.close": "Kamerayı Kapat",
    "demo.scan.or": "— veya hash'i elle girin —",
    "demo.scan.placeholder": "Hash kodunu buraya yapıştırın...",
    "demo.scan.verify": "Doğrula",
    "demo.result.ok.title": "Doğrulandı",
    "demo.result.ok.desc": "Bu sertifika özgündür ve değiştirilmemiştir.",
    "demo.result.fail.title": "Doğrulanamadı",
    "demo.result.fail.desc": "Bu sertifika sistemde bulunamadı. Tedarikçinizden orijinalini isteyin.",
    "demo.result.details": "Sertifika Detayları",
    "demo.result.trust": "Güven Katmanı",
    "demo.result.intact": "Dijital mühür bozulmamış",
    "demo.result.another": "Başka QR Tara",
  }
};

function setLang(lang) {
  localStorage.setItem('agroveri-lang', lang);
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = I18N[lang]?.[key];
    if (val) {
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = val;
      } else {
        el.innerHTML = val;
      }
    }
  });
  // Update switcher buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
}

// Auto-detect on load
(function() {
  const saved = localStorage.getItem('agroveri-lang');
  if (saved) { setLang(saved); return; }
  const browser = navigator.language?.slice(0, 2);
  setLang(browser === 'tr' ? 'tr' : 'en');
})();
