<p align="center">
  <img src="frontend/public/favicon.png" alt="18Mart Portal Logo" width="120" height="120">
</p>

<h1 align="center">🎓 18Mart Portal</h1>

<p align="center">
  <strong>Çanakkale Onsekiz Mart Üniversitesi Öğrenci Portalı</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/FastAPI-0.100-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

<p align="center">
  <a href="#-özellikler">Özellikler</a> •
  <a href="#-kurulum">Kurulum</a> •
  <a href="#-proje-yapısı">Proje Yapısı</a> •
  <a href="#-teknolojiler">Teknolojiler</a> •
  <a href="#-katkıda-bulunma">Katkıda Bulunma</a>
</p>

---

## 📖 Hakkında

**18Mart Portal**, Çanakkale Onsekiz Mart Üniversitesi öğrencileri için tasarlanmış modern ve kullanıcı dostu bir web uygulamasıdır. Öğrencilerin günlük ihtiyaçlarını tek bir platformda karşılamayı hedefler.

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🌤️ **Hava Durumu** | Çanakkale için güncel hava durumu bilgileri |
| 🍽️ **Yemekhane Menüsü** | Günlük yemekhane menüsü ve öğün saatleri |
| 🚌 **Otobüs Saatleri** | Kampüs otobüs hatları ve sefer saatleri |
| 📅 **Akademik Takvim** | Önemli akademik tarihler ve etkinlikler |
| 🌙 **Karanlık Mod** | Göz yormayan dark/light tema desteği |
| 📱 **Responsive Tasarım** | Mobil uyumlu modern arayüz |

## 🚀 Kurulum

### Gereksinimler

- **Node.js** v18 veya üzeri
- **Python** 3.9 veya üzeri
- **npm** veya **yarn**

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/Neuralninjaa/18Mart_Portal.git
cd 18Mart_Portal
```

### 2. Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Frontend varsayılan olarak `http://localhost:5173` adresinde çalışır.

### 3. Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python -m venv venv

# Aktive et (Windows)
.\venv\Scripts\activate

# Aktive et (Linux/Mac)
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
uvicorn app.main:app --reload
```

Backend varsayılan olarak `http://localhost:8000` adresinde çalışır.

## 📁 Proje Yapısı

```
18Mart_Portal/
├── 📂 frontend/                 # React + TypeScript Frontend
│   ├── 📂 src/
│   │   ├── 📂 components/       # UI Bileşenleri
│   │   │   ├── Weather.tsx      # Hava durumu kartı
│   │   │   ├── Meals.tsx        # Yemekhane menüsü
│   │   │   ├── Bus.tsx          # Otobüs saatleri
│   │   │   ├── Calendar.tsx     # Akademik takvim
│   │   │   └── ThemeToggle.tsx  # Tema değiştirici
│   │   ├── 📂 context/          # React Context (Theme)
│   │   ├── 📂 services/         # API servisleri
│   │   ├── 📂 styles/           # CSS dosyaları
│   │   └── App.tsx              # Ana uygulama
│   └── package.json
│
├── 📂 backend/                  # FastAPI Backend
│   ├── 📂 app/
│   │   ├── 📂 routers/          # API endpoint'leri
│   │   ├── 📂 models/           # Veri modelleri
│   │   ├── 📂 services/         # İş mantığı
│   │   └── main.py              # FastAPI uygulaması
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

## 🛠️ Teknolojiler

### Frontend
- ⚛️ **React 18** - UI kütüphanesi
- 📘 **TypeScript** - Tip güvenliği
- ⚡ **Vite** - Build tool
- 🎨 **CSS3** - Modern stiller ve animasyonlar

### Backend
- 🐍 **Python 3.9+** - Programlama dili
- 🚀 **FastAPI** - Modern web framework
- 📦 **Uvicorn** - ASGI sunucu

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları takip edin:

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

## 📄 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👨‍💻 Geliştirici

<p align="center">
  <a href="https://github.com/Neuralninjaa">
    <img src="https://img.shields.io/badge/GitHub-Neuralninjaa-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
</p>

---

<p align="center">
  ⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
</p>

<p align="center">
  Made with ❤️ for ÇOMÜ Students
</p>
