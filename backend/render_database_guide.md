# Render Veritabanı Kurulum Rehberi

## Seçenek 1: Render PostgreSQL (Önerilen)

### 1. Render'da PostgreSQL Oluşturma
1. Render dashboard'a gidin
2. "New +" -> "PostgreSQL" seçin
3. Ücretsiz plan seçin (256MB limit)
4. Veritabanı adı: `mart_portal`
5. Bağlantı bilgilerini kopyalayın

### 2. Render Environment Variables
```bash
DATABASE_URL=postgresql://username:password@host:5432/mart_portal
SECRET_KEY=your-secret-key-here
```

### 3. Render Deploy
- GitHub reposunu bağlayın
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Seçenek 2: Supabase (Ücretsiz PostgreSQL)

### 1. Supabase Projesi Oluşturma
1. supabase.com'a gidin
2. New Project oluşturun
3. PostgreSQL bağlantı URL'sini alın

### 2. Environment Variables
```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
```

---

## Seçenek 3: Neon (Ücretsiz PostgreSQL)

### 1. Neon Hesabı
1. neon.tech'e gidin
2. Ücretsiz proje oluşturun
3. Connection string'i kopyalayın

### 2. Environment Variables
```bash
DATABASE_URL=postgresql://[user]:[password]@[neon-hostname]/[dbname]?sslmode=require
```

---

## Render için Hazırlık

### 1. requirements.txt Güncelle
```
fastapi
uvicorn
sqlalchemy
pydantic
python-dotenv
httpx
beautifulsoup4
psycopg2-binary
```

### 2. render.yaml Dosyası
```yaml
services:
  - type: web
    name: 18mart-portal
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false  # Render'da manuel ayarlayın
      - key: SECRET_KEY
        sync: false
```

### 3. .env.example Güncelle
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/mart_portal
SECRET_KEY=change-me-in-production
```

---

## Öneri: Render PostgreSQL

**Avantajları:**
- Render ile tam entegrasyon
- Otomatik yönetim
- Ücretsiz plan
- Güvenli bağlantı
- Otomatik yedekleme

**Kurulum:**
1. Render'da PostgreSQL oluştur
2. Bağlantı URL'sini kopyala
3. Render environment variables'a ekle
4. Deploy et
