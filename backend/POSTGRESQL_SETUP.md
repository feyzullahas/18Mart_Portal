# PostgreSQL Kurulum ve Konfigürasyon

## 1. PostgreSQL Kurulumu
Eğer PostgreSQL kurulu değilse:
```bash
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql
# Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib
```

## 2. Veritabanı Oluşturma
```sql
-- PostgreSQL komut satırında (psql)
CREATE DATABASE mart_portal;
CREATE USER mart_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mart_portal TO mart_user;
```

## 3. .env Dosyasını Oluşturma
`.env.example` dosyasını kopyalayın:
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```
DATABASE_URL=postgresql://mart_user:your_password@localhost/mart_portal
SECRET_KEY=your_very_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 4. Python Bağımlılıklarını Yükleme
```bash
pip install -r requirements.txt
```

## 5. Veritabanı Tablolarını Oluşturma
```bash
cd backend
python scripts/create_tables.py
```

## 6. API'yi Başlatma
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/token` - Kullanıcı girişi (JWT token al)
- `POST /users/` - Yeni kullanıcı kaydı
- `GET /users/me` - Mevcut kullanıcı bilgileri
- `PUT /users/me` - Kullanıcı bilgilerini güncelle

### Schedules
- `POST /schedules/` - Yeni ders programı ekle
- `GET /schedules/my` - Kullanıcının kendi ders programı
- `GET /schedules/{id}` - Belirli bir ders programı
- `PUT /schedules/{id}` - Ders programını güncelle
- `DELETE /schedules/{id}` - Ders programını sil

## Örnek Kullanım

### 1. Yeni Kullanıcı Kaydı
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ogrenci1",
    "email": "ogrenci1@mart.edu.tr",
    "full_name": "Öğrenci Bir",
    "student_id": "123456",
    "department": "Bilgisayar Mühendisliği",
    "password": "sifre123"
  }'
```

### 2. Giriş Yapma
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ogrenci1&password=sifre123"
```

### 3. Ders Programı Ekleme
```bash
curl -X POST "http://localhost:8000/schedules/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "course_code": "BLM101",
    "course_name": "Programlamaya Giriş",
    "instructor": "Prof. Dr. Ahmet Yılmaz",
    "classroom": "A101",
    "day_of_week": "Monday",
    "start_time": "09:00:00",
    "end_time": "10:30:00",
    "semester": "Fall",
    "year": 2024
  }'
```
