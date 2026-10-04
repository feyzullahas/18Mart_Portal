# Otobüs Saatleri PDF Sistemi

Otobüs saatleri, Çanakkale Belediyesi Ulaşım Hizmetleri Müdürlüğünün resmi [Hatlar ve Otobüs Saatleri](https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/) sayfasından alınır.

- `api/app/services/bus_service.py` sayfadaki tüm PDF bağlantılarını ve başlıklarını kaynağın sırasıyla alır. Liste 6 saat bellekte tutulur; belediye sayfası geçici olarak erişilemezse son başarılı liste kullanılır.
- `api/app/routers/bus.py` önce son altı saatlik indirilen PDF dosyasını sunar, yoksa resmi kaynağa proxy yapar. Dosyalar ve bağlantı metadata’sı Vercel API dağıtımına eklenir.
- `frontend/src/components/Bus.tsx` belediyenin verdiği PDF başlıklarını aynen gösterir. `PdfViewer.tsx` PDF’i uygulama içinde açar; hata halinde yeni sekmeye yönlendirme yapmaz ve tekrar deneme sunar.
- `.github/workflows/download_bus_schedules.yml` her 6 saatte bir tüm PDF’leri `api/data/bus_schedules/` dizinine indirir ve başlık/kaynak eşleşmelerini metadata dosyalarında saklar.

## Elle yenileme

```powershell
.venv\Scripts\python.exe api\scripts\refresh_bus_schedules.py
```

Farklı bir klasöre indirmek için `--output-dir` verilebilir. Otomatik yenileme GitHub Actions içindeki **Refresh Bus Schedule PDFs** iş akışından elle de başlatılabilir.
