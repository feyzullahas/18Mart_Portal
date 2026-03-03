from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

class CalendarService:
    # Takvim Listesi
    CALENDARS = [
        {"id": "general", "name": "Genel (Önlisans/Lisans)", "category": "general"},
        {"id": "yaz_okulu", "name": "Yaz Okulu", "category": "general"},
        {"id": "tip", "name": "Tıp Fakültesi", "category": "faculty", "has_sub": True}, # has_sub: Alt dönemleri var
        {"id": "dis", "name": "Diş Hekimliği Fakültesi", "category": "faculty"},
        {"id": "hazirlik", "name": "Yabancı Diller (Hazırlık)", "category": "school"},
        {"id": "turizm", "name": "Turizm Fakültesi", "category": "faculty"},
        {"id": "gokceada", "name": "Gökçeada Uygulamalı Bilimler", "category": "school"},
        {"id": "lisansustu", "name": "Lisansüstü Eğitim Enstitüsü", "category": "institute"}
    ]

    # Alt Ktegoriler (Sadece Tıp için şimdilik)
    SUB_CALENDARS = {
        "tip": [
            {"id": "tip_1", "name": "Dönem 1"},
            {"id": "tip_2", "name": "Dönem 2"},
            {"id": "tip_3", "name": "Dönem 3"},
            {"id": "tip_4", "name": "Dönem 4"},
            {"id": "tip_5", "name": "Dönem 5"},
            {"id": "tip_6", "name": "Dönem 6"},
        ]
    }

    # Veritabanı: Start ve End Date birlikte
    EVENTS_DB = {
        "general": [
            {"start": "2025-09-01", "end": "2025-09-03", "title": "Elektronik Kayıtlar", "type": "registration"},
            {"start": "2025-09-01", "end": "2025-09-05", "title": "Yüzyüze Kayıtlar", "type": "registration"},
            {"start": "2025-09-08", "end": "2025-09-08", "title": "Yabancı Dil Seviye Tespit Sınavı", "type": "exam"},
            {"start": "2025-09-09", "end": "2025-09-10", "title": "Yabancı Dil Muafiyet Sınavı", "type": "exam"},
            {"start": "2025-09-08", "end": "2025-09-12", "title": "Kayıt Yenileme", "type": "registration"},
            {"start": "2025-09-15", "end": "2025-09-19", "title": "Ders Ekleme-Bırakma", "type": "registration"},
            {"start": "2025-09-15", "end": "2025-12-26", "title": "Güz Yarıyılı Ders Dönemi", "type": "term"},
            {"start": "2025-11-03", "end": "2025-11-07", "title": "Ara (Vize) Sınavlar", "type": "exam"},
            {"start": "2025-12-29", "end": "2026-01-09", "title": "Final Sınavları", "type": "exam"},
            {"start": "2026-01-19", "end": "2026-01-23", "title": "Bütünleme Sınavları", "type": "exam"},
            {"start": "2026-02-05", "end": "2026-02-05", "title": "Tek Ders Sınavı", "type": "exam"},
            
            # BAHAR
            {"start": "2026-02-09", "end": "2026-02-13", "title": "Bahar Kayıt Yenileme", "type": "registration"},
            {"start": "2026-02-16", "end": "2026-02-20", "title": "Bahar Ders Ekleme-Bırakma", "type": "registration"},
            {"start": "2026-02-16", "end": "2026-06-05", "title": "Bahar Yarıyılı Ders Dönemi", "type": "term"},
            {"start": "2026-04-06", "end": "2026-04-10", "title": "Bahar Ara Sınavlar", "type": "exam"},
            {"start": "2026-06-08", "end": "2026-06-19", "title": "Bahar Final Sınavları", "type": "exam"},
            {"start": "2026-06-29", "end": "2026-07-03", "title": "Bahar Bütünleme Sınavları", "type": "exam"},
            
            # RESMİ TATİLLER (Ders yapılan günler hariç)
            {"start": "2025-10-29", "end": "2025-10-29", "title": "Cumhuriyet Bayramı", "type": "holiday"},
            {"start": "2026-01-01", "end": "2026-01-01", "title": "Yılbaşı Tatili", "type": "holiday"}
        ],

        "yaz_okulu": [
            {"start": "2026-07-06", "end": "2026-07-08", "title": "Geçici Kayıtlar", "type": "registration"},
            {"start": "2026-07-09", "end": "2026-07-10", "title": "Kesin Kayıtlar", "type": "registration"},
            {"start": "2026-07-13", "end": "2026-08-28", "title": "Yaz Okulu Ders Dönemi", "type": "term"},
            {"start": "2026-08-31", "end": "2026-09-04", "title": "Yaz Okulu Sonu Sınavları", "type": "exam"}
        ],

        "tip_1": [
            {"start": "2025-09-01", "end": "2025-09-05", "title": "Dönem 1 Kayıtlar ve Oryantasyon", "type": "registration"},
            {"start": "2025-09-15", "end": "2026-05-22", "title": "Dönem 1 Eğitim Öğretim Yılı", "type": "term"},
            {"start": "2026-01-12", "end": "2026-01-23", "title": "Dönem 1 Ara Tatil", "type": "holiday"},
            {"start": "2026-06-08", "end": "2026-06-12", "title": "Dönem 1 Finaller", "type": "exam"},
            {"start": "2026-06-29", "end": "2026-07-03", "title": "Dönem 1 Bütünleme", "type": "exam"}
        ],
        
        "tip_2": [
            {"start": "2025-08-25", "end": "2025-08-29", "title": "Dönem 2 Kayıt Yenileme", "type": "registration"},
            {"start": "2025-09-01", "end": "2026-05-15", "title": "Dönem 2 Eğitim Öğretim Yılı", "type": "term"},
            {"start": "2026-01-05", "end": "2026-01-16", "title": "Dönem 2 Ara Tatil", "type": "holiday"},
            {"start": "2026-06-01", "end": "2026-06-05", "title": "Dönem 2 Finaller", "type": "exam"},
            {"start": "2026-06-22", "end": "2026-06-26", "title": "Dönem 2 Bütünleme", "type": "exam"}
        ],

        "tip_3": [
            {"start": "2025-08-25", "end": "2025-08-29", "title": "Dönem 3 Kayıt Yenileme", "type": "registration"},
            {"start": "2025-09-01", "end": "2026-05-22", "title": "Dönem 3 Eğitim Öğretim Yılı", "type": "term"},
            {"start": "2026-01-05", "end": "2026-01-16", "title": "Dönem 3 Ara Tatil", "type": "holiday"},
            {"start": "2026-06-08", "end": "2026-06-12", "title": "Dönem 3 Finaller", "type": "exam"},
            {"start": "2026-06-29", "end": "2026-07-03", "title": "Dönem 3 Bütünleme", "type": "exam"}
        ],

        "tip_4": [
            {"start": "2025-08-11", "end": "2025-08-15", "title": "Dönem 4 Kayıt Yenileme", "type": "registration"},
            {"start": "2025-08-18", "end": "2026-06-12", "title": "Dönem 4 Eğitim Öğretim Yılı", "type": "term"},
            {"start": "2026-01-05", "end": "2026-01-16", "title": "Dönem 4 Ara Tatil", "type": "holiday"},
            {"start": "2026-06-29", "end": "2026-07-03", "title": "Dönem 4 Bütünleme", "type": "exam"}
        ],
        
        "tip_5": [
            {"start": "2025-08-11", "end": "2025-08-15", "title": "Dönem 5 Kayıt Yenileme", "type": "registration"},
            {"start": "2025-08-18", "end": "2026-06-12", "title": "Dönem 5 Eğitim Öğretim Yılı", "type": "term"},
            {"start": "2026-01-05", "end": "2026-01-16", "title": "Dönem 5 Ara Tatil", "type": "holiday"},
            {"start": "2026-06-29", "end": "2026-07-03", "title": "Dönem 5 Bütünleme", "type": "exam"}
        ],

        "tip_6": [
            {"start": "2025-06-23", "end": "2025-06-27", "title": "Dönem 6 Kayıt Yenileme", "type": "registration"},
            {"start": "2025-07-01", "end": "2026-06-30", "title": "Dönem 6 Eğitim Öğretim Yılı", "type": "term"}
        ],
        
        "dis": [
            {"start": "2025-09-01", "end": "2025-09-05", "title": "Kayıt Haftası", "type": "registration"},
            {"start": "2025-09-08", "end": "2025-09-12", "title": "Kayıt Yenileme ve Ders Seçimi", "type": "registration"},
            {"start": "2025-09-22", "end": "2026-01-09", "title": "Güz Dönemi", "type": "term"},
            {"start": "2025-11-10", "end": "2025-11-21", "title": "Güz Ara Sınavları", "type": "exam"},
            {"start": "2026-01-12", "end": "2026-01-16", "title": "Güz Final Sınavları", "type": "exam"},
            {"start": "2026-01-26", "end": "2026-01-30", "title": "Güz Bütünleme Sınavları", "type": "exam"},
            {"start": "2026-02-02", "end": "2026-02-06", "title": "Bahar Kayıt Yenileme", "type": "registration"},
            {"start": "2026-02-16", "end": "2026-06-05", "title": "Bahar Dönemi", "type": "term"},
            {"start": "2026-04-06", "end": "2026-04-17", "title": "Bahar Ara Sınavları", "type": "exam"},
            {"start": "2026-06-08", "end": "2026-06-19", "title": "Bahar Final Sınavları", "type": "exam"},
            {"start": "2026-06-29", "end": "2026-07-10", "title": "Bahar Bütünleme Sınavları", "type": "exam"},
            {"start": "2025-09-01", "end": "2026-01-30", "title": "Güz Klinik Uygulamalar", "type": "other"},
            {"start": "2026-02-09", "end": "2026-05-26", "title": "Bahar Klinik Uygulamalar", "type": "other"}
        ],

        "hazirlik": [
            {"start": "2025-09-08", "end": "2025-09-10", "title": "Sınav Haftası (Seviye+Muafiyet)", "type": "exam"},
            {"start": "2025-09-15", "end": "2025-10-31", "title": "1. Kur Dersleri", "type": "term"},
            {"start": "2025-11-03", "end": "2025-11-07", "title": "1. Kur Sınavları", "type": "exam"},
            {"start": "2025-11-17", "end": "2026-01-02", "title": "2. Kur Dersleri", "type": "term"},
            {"start": "2026-01-05", "end": "2026-01-09", "title": "2. Kur Sınavları", "type": "exam"},
            {"start": "2026-01-12", "end": "2026-01-16", "title": "2. Kur Ara Tatili", "type": "holiday"},
            {"start": "2026-02-09", "end": "2026-03-27", "title": "3. Kur Dersleri", "type": "term"},
            {"start": "2026-03-30", "end": "2026-04-03", "title": "3. Kur Sınavları", "type": "exam"},
            {"start": "2026-04-06", "end": "2026-05-22", "title": "4. Kur Dersleri", "type": "term"},
            {"start": "2026-06-02", "end": "2026-06-06", "title": "4. Kur Sınavları", "type": "exam"}
        ]
    }

    def get_calendars(self) -> Dict:
        """Kullanılabilir takvim listesini ve alt kategorileri döndürür"""
        return {
            "calendars": self.CALENDARS,
            "sub_calendars": self.SUB_CALENDARS
        }

    def get_events(self, calendar_id: str = "general") -> Dict:
        """Seçilen takvimin olaylarını döndürür"""
        
        events_list = self.EVENTS_DB.get(calendar_id, [])
        
        # ID'nin ana takvim listesinde veya alt listelerde olup olmadığını bul
        cal_name = ""
        # Ana listede ara
        main_cal = next((c for c in self.CALENDARS if c["id"] == calendar_id), None)
        if main_cal:
            cal_name = main_cal["name"]
        else:
            # Alt listelerde ara
            found = False
            for parent, subs in self.SUB_CALENDARS.items():
                sub = next((s for s in subs if s["id"] == calendar_id), None)
                if sub:
                    cal_name = sub["name"]
                    found = True
                    break
            if not found and events_list:
                cal_name = "Akademik Takvim"

        # Tarihe göre sırala
        sorted_events = sorted(events_list, key=lambda x: x['start'])
        
        # Etkinlikleri işle
        processed_events = []
        today = date.today()
        
        for event in sorted_events:
            try:
                start_date = datetime.strptime(event['start'], "%Y-%m-%d").date()
                end_date = datetime.strptime(event['end'], "%Y-%m-%d").date()
                
                days_left = (start_date - today).days
                
                # Türkçe tarih formatı
                months = {
                    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
                }
                
                processed_events.append({
                    "start": event['start'],
                    "end": event['end'],
                    "title": event['title'],
                    "type": event['type'],
                    "start_formatted": f"{start_date.day} {months[start_date.month]}",
                    "end_formatted": f"{end_date.day} {months[end_date.month]}",
                    "days_left": days_left,
                    "is_past": end_date < today,
                    "is_active": start_date <= today <= end_date
                })
            except ValueError:
                continue 
        
        return {
            "id": calendar_id,
            "name": cal_name,
            "events": processed_events
        }

calendar_service = CalendarService()
