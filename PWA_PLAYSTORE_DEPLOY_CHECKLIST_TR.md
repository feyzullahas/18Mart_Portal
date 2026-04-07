# 18 Mart Portal PWA ve Play Store Yayin Checklist'i

Bu dokuman projede PWA kurulumundan Play Store yuklemesine kadar tek akista izlenecek adimlari verir.

## 1) PWA Kurulum Durumu (Tamamlandi)

Asagidaki dosyalar aktif:
- frontend/public/manifest.json
- frontend/index.html
- frontend/public/sw.js
- frontend/public/offline.html
- frontend/src/main.tsx
- frontend/src/components/InstallPrompt.tsx
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/vercel.json

## 2) Test ve Dogrulama

### A. Local production test
1. frontend klasorunde su komutlari calistir:
   - npm run build
   - npm run preview
2. Tarayicida ac:
   - http://localhost:4173
3. DevTools > Application > Service Workers:
   - sw.js status: activated and is running
4. DevTools > Application > Manifest:
   - name, short_name, icons, start_url dolu olmali
5. DevTools > Application > Cache Storage:
   - portal-static-v2 ve portal-runtime-v2 gorunmeli

### B. Offline testi
1. DevTools > Network > Offline sec
2. Sayfayi yenile
3. Navigasyon isteginde offline fallback sayfasi gorunmeli
4. Daha once ziyaret edilen statik varliklar cache'ten yuklenmeli

### C. Telefonda A2HS testi
1. Siteyi Android Chrome ile ac
2. Biraz gezindikten sonra menude "Ana ekrana ekle" veya "Uygulamayi yukle" secenegi cikmali
3. Uygulama ikonundan acildiginda tarayici adres cubugu olmadan (standalone) acilmali

## 3) Hata ve Debug Playbook

### Service worker gorunmuyor
- Kontrol:
  - Site HTTPS mi?
  - URL ayni origin mi?
  - Production modda mi? (main.tsx yalnizca PROD'da register eder)
- Cozum:
  - Vercel deployment'ta frontend proje koku dogru secili olmali
  - Hard reload yap
  - Application > Service Workers > Unregister > tekrar ac

### /sw.js 404
- Kontrol:
  - Dosya konumu kesinlikle frontend/public/sw.js olmali
  - register yolu /sw.js olmali
- Cozum:
  - Vercel output'ta sw.js yayinlaniyor mu kontrol et
  - Yanlis base path varsa vite config'te base ayarini kontrol et

### Cache stale veri
- Cozum:
  - sw.js icinde CACHE_VERSION arttir (ornek: v2 -> v3)
  - DevTools > Application > Clear storage > Clear site data
  - Deployment sonrasi yeni SW'nin activate olmasini bekle

### Vercel sonrasi dikkat
- /sw.js icin no-cache header aktif olmali
- manifest ve offline sayfasi dogru serve edilmeli
- Her release sonrasi PWA smoke test yapilmali

## 4) Play Store (PWABuilder ile AAB)

### A. AAB olusturma
1. https://www.pwabuilder.com ac
2. Site URL: https://18martportal.tech/
3. Analyze et ve tum mandatory hatalari kapat
4. Android paket olustururken su bilgileri doldur:
   - Package ID: com.onsekizmart.portal (ornek)
   - App name: 18 Mart Portal
   - Version code: her release'te artmali
   - Version name: semver format (1.0.0 gibi)
5. Cikti olarak AAB indir

### B. Google Play Console yukleme
1. Yeni uygulama olustur
2. App access, Content rating, Data safety, Target audience bolumlerini doldur
3. Production release > Create new release > AAB yukle
4. Store listing alanlarini doldur:
   - Kisa aciklama
   - Uzun aciklama
   - Ekran goruntuleri (telefon icin zorunlu)
   - App icon (512x512)
   - Feature graphic (1024x500)
5. Privacy Policy URL ekle (zorunlu)
6. Release'i review'a gonder

## 5) Reddedilmemek icin kritik kontroller

- Uygulama acilisinda bos ekran veya hatali route olmamali
- Login varsa test hesabi veya aciklama notu eklenmeli
- Gizlilik politikasi gercek ve erisilebilir URL olmali
- Cok sik coken endpoint veya timeout olmamali
- Uygulama ikonu net ve policy'ye uygun olmali
- Store listing'te alakasiz anahtar kelime spam'i olmamali

## 6) Bonus Ozellik Durumu

Tamamlandi:
- Offline fallback sayfasi (frontend/public/offline.html)
- Manuel install prompt butonu (InstallPrompt)
- Basic performans iyilestirmesi: static/runtime cache stratejisi

Opsiyonel bir sonraki adimlar:
- route bazli cache stratejisi (API endpoint bazli)
- rollup manualChunks ile JS paket bolme
- install prompt analitik event takibi
