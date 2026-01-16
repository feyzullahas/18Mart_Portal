# 18Mart Portal

Bu proje, 18 Mart Üniversitesi öğrencileri için geliştirilen bir öğrenci portalıdır.

## Proje Yapısı

Proje iki ana bölümden oluşur:

### 1. Frontend (`/frontend`)
React, Vite ve TypeScript kullanılarak geliştirilmiştir.

**Önemli Klasörler:**
- `src/components`: UI bileşenleri (Button, Navbar, vs.)
- `src/pages`: Uygulama sayfaları (Home, Login, vs.)
- `src/services`: Backend API ile iletişim kuran servisler
- `src/utils`: Yardımcı fonksiyonlar
- `src/assets`: Resimler ve statik dosyalar
- `src/styles`: Global stiller

**Kurulum:**
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend (`/backend`)
FastAPI (Python) kullanılarak geliştirilmiştir. Veritabanı olarak SQLite kullanılır.

**Önemli Klasörler:**
- `app/routers`: API endpoint tanımları
- `app/models`: Veritabanı şemaları (SQLAlchemy veya Pydantic)
- `app/services`: İş mantığı katmanı
- `app/utils`: Yardımcı araçlar

**Kurulum:**
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Gereksinimler

- Node.js (v18+)
- Python (3.9+)
